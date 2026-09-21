from __future__ import annotations

import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from notifications.utils import notify_order_transition

logger = logging.getLogger(__name__)

# Timeout for driver to accept/reject before auto-routing to next (seconds)
# For demo, 30 seconds; in production, maybe 60-120s. Use 30 for quick testing.
DISPATCH_TIMEOUT_SECONDS = 30

# For tests with CELERY_TASK_ALWAYS_EAGER, we can set to 0 to run immediately? But we want to simulate timeout.
# We use countdown in apply_async, which in eager mode still respects countdown via threading.

User = get_user_model()


def _get_available_drivers():
    """Return ordered list of available drivers for round-robin. Ordered by id for determinism, or by rating."""
    # Available drivers are those with role=driver and is_active True, ordered by id (round-robin baseline)
    # In production, could order by is_available, rating, current_orders_count, etc.
    return list(User.objects.filter(role='driver', is_active=True).order_by('id'))


def _get_next_driver_index(order, current_index: int) -> int | None:
    queue = order.dispatch_queue or []
    if not queue:
        return None
    # Next index is (current_index + 1) % len(queue) — loops back
    return (current_index + 1) % len(queue)


@shared_task(bind=True, max_retries=0)
def dispatch_order(self, order_id: int):
    """
    Entry point when admin clicks 'Ready' on a processing order.
    Sets up round-robin queue and alerts first driver.
    """
    from orders.models import Order

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning(f"Dispatch: order {order_id} not found")
        return

    if order.status != Order.Status.PROCESSING:
        logger.warning(f"Dispatch: order {order.order_number} not in processing, status={order.status}")
        return

    if order.dispatch_in_progress:
        logger.info(f"Dispatch: order {order.order_number} already dispatching")
        return

    drivers = _get_available_drivers()
    if not drivers:
        logger.warning(f"Dispatch: no available drivers for {order.order_number}")
        # Could notify admin that no drivers available
        return

    # Build queue as list of driver IDs in order
    queue = [d.id for d in drivers]
    order.dispatch_queue = queue
    order.dispatch_current_index = 0
    order.dispatch_in_progress = True
    order.dispatch_status = Order.DispatchStatus.DISPATCHING
    # Do not change main status yet; keep as processing until accepted
    # is_locked remains False until accept
    order.save(update_fields=['dispatch_queue', 'dispatch_current_index', 'dispatch_in_progress', 'dispatch_status', 'updated_at'])

    # Alert first driver
    first_driver_id = queue[0]
    try:
        first_driver = User.objects.get(pk=first_driver_id)
    except User.DoesNotExist:
        logger.error(f"Dispatch: first driver {first_driver_id} not found")
        return

    # Set current dispatch driver
    order.driver = first_driver  # temporary assignment for visibility, but not yet locked
    order.save(update_fields=['driver'])

    # Create notification for driver: incoming order alert
    try:
        from notifications.models import Notification
        Notification.objects.create(
            user=first_driver,
            order=order,
            kind='assignment',
            title=f'New Assignment: {order.order_number}',
            message=f'You have a new order {order.order_number} from {order.origin} → {order.destination}. Tap Accept or Reject.',
            stage_from='processing',
            stage_to='dispatching',
        )
        # Also notify admin that dispatch started
        for admin in User.objects.filter(role='admin'):
            Notification.objects.create(
                user=admin,
                order=order,
                kind='assignment',
                title=f'Dispatch started: {order.order_number}',
                message=f'Dispatching {order.order_number} to {first_driver.get_full_name() or first_driver.email} (1/{len(queue)})',
                stage_from='processing',
                stage_to='dispatching',
            )
    except Exception as e:
        logger.warning(f"Dispatch notification failed: {e}")

    # Schedule timeout for this driver (skip in eager/test mode to avoid immediate loop)
    from django.conf import settings
    if not getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
        handle_driver_timeout.apply_async(
            args=[order.id, first_driver_id, 0],
            countdown=DISPATCH_TIMEOUT_SECONDS,
        )
        logger.info(f"Dispatched {order.order_number} to driver {first_driver.email} (0/{len(queue)-1}) with {DISPATCH_TIMEOUT_SECONDS}s timeout")
    else:
        logger.info(f"Dispatched {order.order_number} to driver {first_driver.email} (0/{len(queue)-1}) eager mode — timeout not scheduled")


@shared_task(bind=True, max_retries=0)
def handle_driver_timeout(self, order_id: int, expected_driver_id: int, expected_index: int):
    """
    Called after DISPATCH_TIMEOUT_SECONDS if driver hasn't responded.
    If order still dispatching and current driver is still the expected one, route to next.
    """
    from orders.models import Order

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return

    # If no longer dispatching, or already assigned/locked, ignore
    if not order.dispatch_in_progress or order.is_locked:
        logger.info(f"Timeout: order {order.order_number} no longer dispatching or locked, ignoring")
        return

    # If status is already received_by_driver, ignore (already accepted)
    if order.status == Order.Status.RECEIVED_BY_DRIVER:
        return

    # If current driver is not the expected one (already moved), ignore stale timeout
    current_driver_id = order.driver_id
    current_index = order.dispatch_current_index
    if current_driver_id != expected_driver_id or current_index != expected_index:
        logger.info(f"Timeout: order {order.order_number} driver/index mismatch (expected {expected_driver_id}/{expected_index}, got {current_driver_id}/{current_index}), ignoring stale timeout")
        return

    # Check if order is still in a state where dispatch makes sense (processing/received)
    if order.status not in (Order.Status.PROCESSING, Order.Status.RECEIVED):
        logger.info(f"Timeout: order {order.order_number} status {order.status} not in dispatchable, ignoring")
        return

    # Driver timed out or implicitly rejected — move to next
    queue = order.dispatch_queue or []
    if not queue:
        return

    next_index = (expected_index + 1) % len(queue)
    # If we looped back to 0 and all have been tried, we still continue looping per spec: "If all reject, it loops back to the 1st driver"
    # So we always continue, even after full loop, unless order is cancelled or accepted
    next_driver_id = queue[next_index]

    try:
        next_driver = User.objects.get(pk=next_driver_id)
    except User.DoesNotExist:
        logger.error(f"Timeout: next driver {next_driver_id} not found")
        return

    # Update order to next driver
    order.dispatch_current_index = next_index
    order.driver = next_driver
    order.save(update_fields=['dispatch_current_index', 'driver', 'updated_at'])

    # Notify next driver
    try:
        from notifications.models import Notification
        Notification.objects.create(
            user=next_driver,
            order=order,
            kind='assignment',
            title=f'New Assignment: {order.order_number}',
            message=f'You have a new order {order.order_number} from {order.origin} → {order.destination}. Previous driver timed out. Tap Accept or Reject.',
            stage_from='dispatching',
            stage_to='dispatching',
        )
        # Notify admin of auto-routing
        for admin in User.objects.filter(role='admin'):
            Notification.objects.create(
                user=admin,
                order=order,
                kind='assignment',
                title=f'Auto-routed: {order.order_number}',
                message=f'{order.order_number} timed out for driver {expected_driver_id}, auto-routed to {next_driver.email} ({next_index+1}/{len(queue)})',
                stage_from='dispatching',
                stage_to='dispatching',
            )
    except Exception as e:
        logger.warning(f"Timeout notification failed: {e}")

    # Schedule next timeout (skip in eager/test mode)
    from django.conf import settings
    if not getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
        handle_driver_timeout.apply_async(
            args=[order.id, next_driver_id, next_index],
            countdown=DISPATCH_TIMEOUT_SECONDS,
        )
        logger.info(f"Timeout: {order.order_number} moved from driver {expected_driver_id} to {next_driver_id} ({next_index})")
    else:
        logger.info(f"Timeout: {order.order_number} moved from driver {expected_driver_id} to {next_driver_id} ({next_index}) eager mode — next timeout not scheduled")


@shared_task
def handle_driver_action(order_id: int, driver_id: int, action: str):
    """
    Optional helper for driver Accept/Reject via task (not directly used, but for consistency).
    The actual Accept/Reject is handled synchronously in views, but this task can be used for async.
    """
    pass
