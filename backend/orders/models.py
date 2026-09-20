from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Order(models.Model):
    """
    B2B Logistics Order with strict state-machine enforcement.
    Stage 1: Received (Order Received / استلام الطلب) — only cancellable stage
    Stage 2: Picked Up
    Stage 3: In Transit
    Stage 4: Out for Delivery
    Stage 5: Delivered
    Terminal: Cancelled (only from Stage 1, triggers refund)
    """

    class Status(models.TextChoices):
        RECEIVED = 'received', 'Received (Stage 1 — استلام الطلب)'
        PICKED_UP = 'picked_up', 'Picked Up (Stage 2)'
        IN_TRANSIT = 'in_transit', 'In Transit (Stage 3)'
        OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery (Stage 4)'
        DELIVERED = 'delivered', 'Delivered (Stage 5)'
        CANCELLED = 'cancelled', 'Cancelled'

    # Frontend alias mapping: shipment `order_received`/`booked` → `received`
    LEGACY_STATUS_MAP = {
        'order_received': Status.RECEIVED,
        'booked': Status.RECEIVED,
    }

    order_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Human readable order number e.g. SHP-10001-ORD',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role': 'user'},
        help_text='Customer who owns the order (role=user)',
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driver_orders',
        limit_choices_to={'role': 'driver'},
        help_text='Assigned driver (role=driver), set via dispatch board',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
        db_index=True,
    )

    # Core logistics fields — minimal for state machine, extensible
    origin = models.CharField(max_length=120, default='Rotterdam')
    origin_code = models.CharField(max_length=10, default='RTM')
    destination = models.CharField(max_length=120, default='Chicago')
    destination_code = models.CharField(max_length=10, default='ORD')
    mode = models.CharField(max_length=30, default='Ocean Freight')
    priority = models.CharField(max_length=30, default='Standard Freight')
    gross_weight = models.CharField(max_length=30, default='12,400 kg')

    # Cancellation / refund tracking (Stage 1 only)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_orders',
    )
    refund_status = models.CharField(
        max_length=10,
        choices=[('none', 'None'), ('pending', 'Pending'), ('refunded', 'Refunded')],
        default='none',
        db_index=True,
    )
    refund_id = models.CharField(max_length=64, null=True, blank=True)
    invoice_id = models.CharField(max_length=20, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        help_text='Original Visa PaymentIntent (pi_...) for Stripe refund',
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # State machine: allowed forward transitions + driver reject revert
    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        Status.RECEIVED: {Status.PICKED_UP, Status.CANCELLED},
        Status.PICKED_UP: {Status.IN_TRANSIT, Status.RECEIVED},  # RECEIVED via driver reject (return to pool)
        Status.IN_TRANSIT: {Status.OUT_FOR_DELIVERY},
        Status.OUT_FOR_DELIVERY: {Status.DELIVERED},
        Status.DELIVERED: set(),
        Status.CANCELLED: set(),
    }

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'order'
        verbose_name_plural = 'orders'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=[
                    'received', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'cancelled'
                ]),
                name='order_status_valid',
                violation_error_message='Invalid order status',
            ),
        ]
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['owner', 'status']),
        ]

    def __str__(self) -> str:
        return f'{self.order_number} — {self.get_status_display()}'

    @property
    def is_cancellable(self) -> bool:
        return self.status == self.Status.RECEIVED

    def can_transition(self, new_status: str) -> bool:
        # Normalize legacy aliases
        new_status = self.LEGACY_STATUS_MAP.get(new_status, new_status)
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, set())
        return new_status in allowed

    def clean(self):
        # Enforce driver must be driver role if set
        if self.driver_id and getattr(self.driver, 'role', None) not in (None, 'driver'):
            if hasattr(self.driver, 'role') and self.driver.role != 'driver':
                raise ValidationError({'driver': 'Driver must have role=driver'})
        # Validate state-machine transition when updating existing order
        if self.pk:
            try:
                old = type(self).objects.get(pk=self.pk)
                if old.status != self.status:
                    # Normalize legacy aliases for comparison
                    new_status = self.LEGACY_STATUS_MAP.get(self.status, self.status)
                    old_status = self.LEGACY_STATUS_MAP.get(old.status, old.status)
                    if old_status != new_status and not old.can_transition(new_status):
                        raise ValidationError({
                            'status': f'Invalid transition {old.get_status_display()} -> {self.get_status_display()}. '
                                      f'Allowed: {", ".join(sorted(old.ALLOWED_TRANSITIONS.get(old.status, set()))) or "none (terminal)"}'
                        })
                    # Extra guard: cancellation only from Stage 1
                    if new_status == self.Status.CANCELLED and old_status != self.Status.RECEIVED:
                        raise ValidationError({'status': 'Only orders in Stage 1 (Received) can be cancelled'})
            except type(self).DoesNotExist:
                pass

    def save(self, *args, **kwargs):
        # Auto-generate mock Visa PaymentIntent for new orders (for refund demo)
        if not self.stripe_payment_intent_id:
            # Deterministic mock PI based on order_number for idempotency
            suffix = self.order_number.replace('-', '').lower()[-12:] or 'test'
            self.stripe_payment_intent_id = f'pi_{suffix}_mock_visa'
        # Auto-populate cancellation / refund metadata when transitioning to cancelled
        if self.status == self.Status.CANCELLED:
            if not self.cancelled_at:
                from django.utils import timezone
                self.cancelled_at = timezone.now()
            if self.refund_status == 'none':
                self.refund_status = 'pending'
            if not self.invoice_id:
                # Generate invoice id if missing
                self.invoice_id = f'INV-{self.order_number[-4:]}' if len(self.order_number) >= 4 else 'INV-0000'
        self.full_clean(exclude=None)
        super().save(*args, **kwargs)
