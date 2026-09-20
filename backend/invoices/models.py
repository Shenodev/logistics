from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'
        REFUNDED = 'refunded', 'Refunded'
        CANCELLED = 'cancelled', 'Cancelled'

    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Human readable invoice e.g. INV-2024-10004',
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text='Linked order, if any',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices',
        help_text='Owner of the invoice',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Invoice amount in USD',
    )
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    refund_id = models.CharField(max_length=64, null=True, blank=True, help_text='Stripe refund ID if refunded')
    stripe_payment_intent_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        help_text='Original Visa PaymentIntent (pi_...) for refund',
    )
    description = models.CharField(max_length=200, blank=True, help_text='e.g. Ocean Freight · SHP-10001-ORD')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'invoice'
        verbose_name_plural = 'invoices'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name='invoice_amount_non_negative',
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=['pending', 'paid', 'overdue', 'refunded', 'cancelled']),
                name='invoice_status_valid',
            ),
        ]
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self) -> str:
        return f'{self.invoice_number} — {self.get_status_display()} — ${self.amount}'

    @property
    def is_refunded(self) -> bool:
        return self.status == self.Status.REFUNDED
