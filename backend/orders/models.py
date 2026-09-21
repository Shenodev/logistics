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
        PROCESSING = 'processing', 'Processing (قيد التنفيذ) — Stage 0'
        RECEIVED = 'received', 'Received (Stage 1 — استلام الطلب)'
        PICKED_UP = 'picked_up', 'Picked Up (Stage 2)'
        IN_TRANSIT = 'in_transit', 'In Transit (Stage 3)'
        OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery (Stage 4)'
        DELIVERED = 'delivered', 'Delivered (Stage 5)'
        CANCELLED = 'cancelled', 'Cancelled'
        RECEIVED_BY_DRIVER = 'received_by_driver', 'Received by Driver (مستلم من السائق)'

    # Dispatch state for automated round-robin
    class DispatchStatus(models.TextChoices):
        IDLE = 'idle', 'Idle'
        DISPATCHING = 'dispatching', 'Dispatching'
        ASSIGNED = 'assigned', 'Assigned to Driver'
        COMPLETED = 'completed', 'Completed'

    # Frontend alias mapping: shipment `order_received`/`booked` → `received`, processing is Stage 0
    LEGACY_STATUS_MAP = {
        'order_received': Status.RECEIVED,
        'booked': Status.RECEIVED,
        'processing': Status.PROCESSING,
        'قيد التنفيذ': Status.PROCESSING,
        'received_by_driver': Status.RECEIVED_BY_DRIVER,
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
        help_text='Customer who owns the order',
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
        default=Status.PROCESSING,
        db_index=True,
    )

    # Automated dispatch engine fields
    dispatch_status = models.CharField(
        max_length=20,
        choices=DispatchStatus.choices,
        default=DispatchStatus.IDLE,
        db_index=True,
        help_text='Round-robin dispatch state',
    )
    dispatch_queue = models.JSONField(
        default=list,
        blank=True,
        help_text='Ordered list of driver IDs for round-robin',
    )
    dispatch_current_index = models.IntegerField(default=0)
    dispatch_in_progress = models.BooleanField(default=False, db_index=True)
    is_locked = models.BooleanField(
        default=False,
        db_index=True,
        help_text='When True, Cancel is disabled globally (after driver Accept)',
    )
    # When received_by_driver, store accepted driver snapshot for visibility
    assigned_driver_name = models.CharField(max_length=120, blank=True, default='')
    assigned_driver_phone = models.CharField(max_length=20, blank=True, default='')

    # Core logistics fields — minimal for state machine, extensible
    origin = models.CharField(max_length=120, default='Rotterdam')
    origin_code = models.CharField(max_length=10, default='RTM')
    destination = models.CharField(max_length=120, default='Chicago')
    destination_code = models.CharField(max_length=10, default='ORD')
    mode = models.CharField(max_length=30, default='Ocean Freight')
    priority = models.CharField(max_length=30, default='Standard Freight')
    gross_weight = models.CharField(max_length=30, default='12,400 kg')
    # Delivery-specific fields for API integration (Restaurant/Pickup & Customer/Dropoff + live status)
    customer_phone = models.CharField(max_length=20, default='+1 (212) 555-0148')
    restaurant_name = models.CharField(max_length=120, default='Rotterdam Hub Kitchen')
    restaurant_address = models.CharField(max_length=200, default='Rotterdam, RTM • Bay 04 • Pickup Dock 4')
    delivery_status = models.CharField(
        max_length=20,
        choices=[('assigned', 'Assigned'), ('picked_up', 'Picked Up'), ('on_the_way', 'On the Way'), ('delivered', 'Delivered')],
        default='assigned',
        db_index=True,
        help_text='Driver delivery status, cycles assigned→picked_up→on_the_way→delivered',
    )
    delivery_updated_at = models.DateTimeField(null=True, blank=True)

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

    # State machine: allowed forward transitions + driver reject revert + new dispatch flow
    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        Status.PROCESSING: {Status.RECEIVED, Status.CANCELLED, Status.RECEIVED_BY_DRIVER},
        Status.RECEIVED: {Status.PICKED_UP, Status.CANCELLED, Status.RECEIVED_BY_DRIVER},
        Status.PICKED_UP: {Status.IN_TRANSIT, Status.RECEIVED},  # RECEIVED via driver reject (return to pool)
        Status.IN_TRANSIT: {Status.OUT_FOR_DELIVERY},
        Status.OUT_FOR_DELIVERY: {Status.DELIVERED},
        Status.DELIVERED: set(),
        Status.CANCELLED: set(),
        Status.RECEIVED_BY_DRIVER: {Status.PICKED_UP, Status.IN_TRANSIT, Status.DELIVERED},
    }

    DELIVERY_ALLOWED: dict[str, set[str]] = {
        'assigned': {'picked_up'},
        'picked_up': {'on_the_way'},
        'on_the_way': {'delivered'},
        'delivered': set(),
    }

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'order'
        verbose_name_plural = 'orders'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=[
                    'processing', 'received', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'cancelled', 'received_by_driver'
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
        if self.is_locked:
            return False
        return self.status in (self.Status.PROCESSING, self.Status.RECEIVED)

    def can_transition(self, new_status: str) -> bool:
        # Normalize legacy aliases
        new_status = self.LEGACY_STATUS_MAP.get(new_status, new_status)
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, set())
        return new_status in allowed

    def can_transition_delivery(self, new: str) -> bool:
        return new in self.DELIVERY_ALLOWED.get(self.delivery_status, set())

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
                    # Allow delivery completion to sync main status to delivered even from in_transit (bypass intermediate)
                    is_delivery_completion = (
                        self.delivery_status == 'delivered' and new_status == self.Status.DELIVERED
                    )
                    if old_status != new_status and not is_delivery_completion and not old.can_transition(new_status):
                        raise ValidationError({
                            'status': f'Invalid transition {old.get_status_display()} -> {self.get_status_display()}. '
                                      f'Allowed: {", ".join(sorted(old.ALLOWED_TRANSITIONS.get(old.status, set()))) or "none (terminal)"}'
                        })
                    # Extra guard: cancellation only from Stage 1
                    if new_status == self.Status.CANCELLED and old_status != self.Status.RECEIVED:
                        raise ValidationError({'status': 'Only orders in Stage 1 (Received) can be cancelled'})
                if old.delivery_status != self.delivery_status:
                    if not old.can_transition_delivery(self.delivery_status):
                        raise ValidationError({
                            'delivery_status': f'Invalid delivery transition {old.delivery_status} -> {self.delivery_status}. '
                                               f'Allowed: {", ".join(sorted(old.DELIVERY_ALLOWED.get(old.delivery_status, set()))) or "none"}'
                        })
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
        # Auto-update delivery timestamp when delivery_status changes and sync main status for user timeline
        if self.pk:
            try:
                old = type(self).objects.get(pk=self.pk)
                if old.delivery_status != self.delivery_status:
                    from django.utils import timezone
                    self.delivery_updated_at = timezone.now()
                    # Sync main order status for user tracking timeline (instant reflect via polling)
                    delivery_to_status = {
                        'picked_up': self.Status.PICKED_UP,
                        'on_the_way': self.Status.IN_TRANSIT,
                        'delivered': self.Status.DELIVERED,
                    }
                    mapped = delivery_to_status.get(self.delivery_status)
                    if mapped and mapped != self.status:
                        # Allow delivery completion to set main status to delivered even if intermediate
                        if mapped == self.Status.DELIVERED:
                            self.status = mapped
                        elif old.can_transition(mapped):
                            self.status = mapped
            except type(self).DoesNotExist:
                pass
        elif self.delivery_status != 'assigned':
            from django.utils import timezone
            self.delivery_updated_at = timezone.now()
        self.full_clean(exclude=None)
        # Capture previous state for notification (before super().save sets pk for creates)
        is_new = self._state.adding
        old_status = None
        old_delivery = None
        if not is_new and self.pk:
            try:
                _old = type(self).objects.get(pk=self.pk)
                old_status = _old.status
                old_delivery = _old.delivery_status
            except type(self).DoesNotExist:
                pass
        super().save(*args, **kwargs)
        # Real-time notifications: push on status / delivery_status transitions (Created -> Preparing -> Dispatched -> Delivered)
        # Only for updates, not initial creation (except cancelled initial is still a transition from None)
        try:
            new_status = self.status
            new_delivery = self.delivery_status
            # Determine if this is a meaningful transition
            should_notify = False
            notify_from = None
            notify_to = None
            notify_kind = 'order_status'
            if not is_new and old_status and old_status != new_status:
                should_notify = True
                notify_from = old_status
                notify_to = new_status
            elif not is_new and old_delivery and old_delivery != new_delivery:
                should_notify = True
                notify_from = old_delivery
                notify_to = new_delivery
                notify_kind = 'order_status'
            elif is_new and new_status in ('received', 'cancelled'):
                # Optional: notify on creation as "Created"
                should_notify = False
            if should_notify and notify_from and notify_to:
                from notifications.utils import notify_order_transition
                # Run in try to not block save on notification failure
                try:
                    notify_order_transition(self, notify_from, notify_to, kind=notify_kind)
                except Exception:
                    pass
        except Exception:
            pass
