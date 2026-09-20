from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    Persisted live alert for order stage transitions.
    Pushed instantly via SSE/WebSocket to User and Admin dashboards.
    """

    class Kind(models.TextChoices):
        ORDER_STATUS = 'order_status', 'Order Status'
        REFUND = 'refund', 'Refund'
        ASSIGNMENT = 'assignment', 'Assignment'
        SYSTEM = 'system', 'System'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True,
        help_text='Recipient user (owner or admin)',
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text='Related order, if any',
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.ORDER_STATUS, db_index=True)
    title = models.CharField(max_length=120)
    message = models.TextField(max_length=500)
    stage_from = models.CharField(max_length=20, blank=True, default='')
    stage_to = models.CharField(max_length=20, blank=True, default='')
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
        verbose_name = 'notification'
        verbose_name_plural = 'notifications'

    def __str__(self) -> str:
        return f'{self.user.email} — {self.title} ({self.stage_to})'
