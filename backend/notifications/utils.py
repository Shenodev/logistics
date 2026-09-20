from __future__ import annotations

import logging

from django.contrib.auth import get_user_model

from .models import Notification

logger = logging.getLogger(__name__)

# Human labels for stages — maps backend status to frontend friendly
STAGE_LABELS = {
    'received': 'Received',
    'picked_up': 'Preparing',
    'in_transit': 'Dispatched',
    'out_for_delivery': 'Out for Delivery',
    'delivered': 'Delivered',
    'cancelled': 'Cancelled',
    'assigned': 'Assigned',
    'on_the_way': 'On the Way',
}

# Map order status transitions to notification titles
# e.g. Created -> Preparing -> Dispatched -> Delivered
TRANSITION_TITLES = {
    ('received', 'picked_up'): 'Order Preparing',
    ('picked_up', 'in_transit'): 'Order Dispatched',
    ('in_transit', 'out_for_delivery'): 'Out for Delivery',
    ('out_for_delivery', 'delivered'): 'Order Delivered',
    ('received', 'cancelled'): 'Order Cancelled',
    ('assigned', 'picked_up'): 'Order Picked Up',
    ('picked_up', 'on_the_way'): 'On The Way',
    ('on_the_way', 'delivered'): 'Order Delivered',
}


def _build_message(order, stage_from: str, stage_to: str) -> tuple[str, str]:
    label_from = STAGE_LABELS.get(stage_from, stage_from.replace('_', ' ').title())
    label_to = STAGE_LABELS.get(stage_to, stage_to.replace('_', ' ').title())
    key = (stage_from, stage_to)
    title = TRANSITION_TITLES.get(key, f'Order {label_to}')
    # Example: "SHP-10001-ORD moved from Received -> Preparing"
    message = f'{order.order_number} moved from {label_from} -> {label_to} - {order.origin} -> {order.destination}'
    return title, message


def notify_order_transition(order, stage_from: str, stage_to: str, *, actor=None, kind: str = 'order_status'):
    """
    Create persisted notifications for the order owner and all admins.
    Called from Order.save() / signals whenever status or delivery_status changes.
    """
    if not stage_from or not stage_to or stage_from == stage_to:
        return []

    title, message = _build_message(order, stage_from, stage_to)
    User = get_user_model()
    recipients = set()

    # Owner always gets notified
    if getattr(order, 'owner_id', None):
        recipients.add(order.owner_id)

    # All admins get notified (for Admin dashboard bell)
    admin_ids = list(User.objects.filter(role='admin').values_list('id', flat=True))
    # Fallback: is_staff admins
    if not admin_ids:
        admin_ids = list(User.objects.filter(is_staff=True).values_list('id', flat=True))
    recipients.update(admin_ids)

    # Driver assigned also gets notified if relevant (optional)
    if getattr(order, 'driver_id', None):
        recipients.add(order.driver_id)

    # Don't notify actor themselves twice? Keep them — they see toast too
    # Create bulk
    notifications = []
    for user_id in recipients:
        try:
            n = Notification.objects.create(
                user_id=user_id,
                order=order,
                kind=kind,
                title=title,
                message=message,
                stage_from=stage_from,
                stage_to=stage_to,
            )
            notifications.append(n)
        except Exception as exc:
            logger.warning("Failed to create notification for user %s order %s: %s", user_id, order.order_number, exc)

    if notifications:
        logger.info("Notifications created for %s %s->%s to %d recipients", order.order_number, stage_from, stage_to, len(notifications))
    return notifications
