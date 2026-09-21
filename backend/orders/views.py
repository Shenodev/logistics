from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAssignedDriverOrAdmin, IsDriverAssignedOrUnassignedPool

from .models import Order
from .serializers import OrderSerializer

import logging

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_number'
    lookup_url_kwarg = 'order_number'

    def get_permissions(self):
        # Strict RBAC per action
        if self.action in ('update', 'partial_update'):
            # Drivers may only update their assigned orders; admins may update any
            # But block admin manual intervention during dispatch loop
            return [IsAuthenticated(), IsAssignedDriverOrAdmin()]
        if self.action in ('accept', 'reject'):
            # Drivers only, on pool or assigned
            return [IsAuthenticated(), IsDriverAssignedOrUnassignedPool()]
        if self.action == 'cancel':
            # Owner or admin (object-level checked inside), but require auth
            return [IsAuthenticated()]
        if self.action in ('ready',):
            return [IsAuthenticated(), IsAdmin()]
        if self.action == 'create':
            # Manual creation blocked for non-admins in perform_create, but keep IsAuthenticated
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related('owner', 'driver', 'cancelled_by').all()
        # Role-aware filtering
        if getattr(user, 'role', None) == 'admin' or getattr(user, 'is_staff', False):
            return qs
        if getattr(user, 'role', None) == 'driver':
            # Drivers see unassigned pool (received, no driver) + their assigned orders + dispatching pool
            return qs.filter(Q(driver=user) | Q(status='received', driver__isnull=True) | Q(status='processing', dispatch_in_progress=True) | Q(status='processing'))
        # Regular users see only their own orders
        return qs.filter(owner=user)

    def update(self, request, *args, **kwargs):
        # Block admin manual intervention during automated dispatch loop
        order = self.get_object()
        if order.dispatch_in_progress:
            return Response(
                {'detail': 'Automated dispatch in progress — admins cannot manually intervene until driver responds. System is auto-routing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if order.is_locked:
            return Response({'detail': 'Order is locked after driver acceptance. No further updates allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.dispatch_in_progress:
            return Response(
                {'detail': 'Automated dispatch in progress — admins cannot manually intervene until driver responds. System is auto-routing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if order.is_locked:
            return Response({'detail': 'Order is locked after driver acceptance.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Enforce No manual order creation for portal users — only admins/external
        # For this task we allow creation but mark as received and set owner
        # To satisfy guardrail, block non-admin manual creation via portal
        user = self.request.user
        if getattr(user, 'role', None) not in ('admin',):
            # Allow creation only if explicitly via external ingestion header
            external = self.request.headers.get('X-External-Ingest') == 'true'
            if not external:
                # Still allow but log; for strict guardrail we could deny:
                # Raise 400 to signal manual creation disabled
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Manual order creation is disabled. Orders are ingested via external APIs.')
        serializer.save(owner=user, status=Order.Status.RECEIVED)

    @action(detail=True, methods=['post'], url_path='ready')
    def ready(self, request, order_number=None):
        """
        Admin triggers Ready on a Processing order, starting the automated round-robin dispatch.
        Uses Celery + Upstash Redis for timeout-driven routing.
        """
        order = self.get_object()
        user = request.user
        # Only admin can trigger Ready
        if getattr(user, 'role', None) != 'admin' and not getattr(user, 'is_staff', False):
            return Response({'detail': 'Only admins can mark orders as Ready.'}, status=status.HTTP_403_FORBIDDEN)
        # Order must be in Processing (قيد التنفيذ) — initial stage
        if order.status != Order.Status.PROCESSING:
            return Response(
                {'detail': f'Only orders in Processing (قيد التنفيذ) can be marked Ready. Current status is {order.get_status_display()} ({order.status}).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if order.dispatch_in_progress:
            return Response({'detail': 'Dispatch already in progress for this order.'}, status=status.HTTP_400_BAD_REQUEST)
        if order.is_locked:
            return Response({'detail': 'Order is locked and cannot be dispatched.'}, status=status.HTTP_400_BAD_REQUEST)

        # Trigger Celery dispatch (Upstash Redis broker)
        try:
            from .tasks import dispatch_order
            # Use eager mode fallback if no broker (tests)
            dispatch_order.delay(order.id)
        except Exception as e:
            logger.warning(f"Celery dispatch failed for {order.order_number}, falling back to sync: {e}")
            # Fallback synchronous dispatch for dev without Redis
            try:
                from .tasks import dispatch_order as sync_dispatch
                sync_dispatch(order.id)
            except Exception as inner:
                return Response({'detail': f'Dispatch failed: {inner}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Refresh and return
        order.refresh_from_db()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, order_number=None):
        order = self.get_object()
        # Global lock check: once driver Accept locks order, Cancel is disabled globally
        if order.is_locked:
            return Response(
                {'detail': 'Order is locked after driver acceptance. Cancel is disabled globally.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Strict Stage 1 check — must be exactly Received OR Processing (initial)
        # Allow cancellation from Processing or Received (Stage 1)
        if order.status not in (Order.Status.RECEIVED, Order.Status.PROCESSING):
            return Response(
                {'detail': f'Only orders in Stage 1 (Received/Processing) can be cancelled. Current status is {order.get_status_display()}.',
                 'status': order.status},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Also check is_cancellable (which includes is_locked)
        if not order.is_cancellable:
            return Response({'detail': 'Order cannot be cancelled at this stage or is locked.'}, status=status.HTTP_400_BAD_REQUEST)
        # Only owner or admin can cancel
        user = request.user
        is_owner = order.owner_id == user.id
        is_admin = getattr(user, 'role', None) == 'admin' or getattr(user, 'is_staff', False)
        if not (is_owner or is_admin):
            return Response({'detail': 'Only the order owner or an admin can cancel this order.'}, status=status.HTTP_403_FORBIDDEN)

        # Perform cancellation — model save will set refund_status=pending etc.
        order.status = Order.Status.CANCELLED
        order.cancelled_by = user
        # cancelled_at, refund_status, invoice_id handled in model save()
        # Also clear dispatch state
        order.dispatch_in_progress = False
        order.dispatch_status = Order.DispatchStatus.IDLE
        try:
            order.save()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Trigger transactional email: order cancelled (from hello@contact.logistics.shenodev.tech)
        try:
            from utils.emails import send_order_cancelled_email
            # Refresh to ensure owner relation is available for email
            order.refresh_from_db()
            # Use select_related for owner email if needed, but order already has owner_id; fetch owner
            if not hasattr(order, 'owner') or order.owner is None:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    order.owner = User.objects.get(pk=order.owner_id)
                except User.DoesNotExist:
                    pass
            send_order_cancelled_email(order)
        except Exception as e:
            # Email failure should not block cancellation
            logger.warning("Failed to send cancelled email for %s: %s", order.order_number, e)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, order_number=None):
        order = self.get_object()
        user = request.user
        if getattr(user, 'role', None) != 'driver':
            return Response({'detail': 'Only drivers can accept orders.'}, status=status.HTTP_403_FORBIDDEN)
        # Must be dispatching and this driver is current in round-robin
        if order.dispatch_in_progress:
            # Verify this driver is the current dispatch target
            queue = order.dispatch_queue or []
            if queue:
                expected_id = queue[order.dispatch_current_index % len(queue)] if queue else None
                if expected_id != user.id:
                    return Response({'detail': 'Not your turn in dispatch queue. Waiting for current driver.'}, status=status.HTTP_403_FORBIDDEN)
            elif order.driver_id and order.driver_id != user.id:
                return Response({'detail': 'Order already assigned to another driver.'}, status=status.HTTP_409_CONFLICT)
        else:
            # Fallback for non-dispatch orders (legacy): must be received
            if order.status not in (Order.Status.PROCESSING, Order.Status.RECEIVED):
                return Response(
                    {'detail': f'Only orders in Processing/Received can be accepted. Current status is {order.get_status_display()}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if order.driver_id and order.driver_id != user.id:
                return Response({'detail': 'Order already assigned to another driver.'}, status=status.HTTP_409_CONFLICT)

        if order.is_locked:
            return Response({'detail': 'Order is locked after acceptance.'}, status=status.HTTP_400_BAD_REQUEST)

        # Strict transition to Received by Driver and lock
        try:
            # Set driver and lock, update status strictly
            order.driver = user
            order.status = Order.Status.RECEIVED_BY_DRIVER
            order.delivery_status = 'assigned'  # keep delivery as assigned, or set to picked_up? Use assigned for lock
            order.is_locked = True
            order.dispatch_in_progress = False
            order.dispatch_status = Order.DispatchStatus.ASSIGNED
            # Snapshot for visibility to User/Admin tracking
            order.assigned_driver_name = user.get_full_name() or user.first_name or user.username
            # Try to get phone from driver profile
            try:
                profile = getattr(user, 'driver_profile', None)
                if profile and getattr(profile, 'phone', None):
                    order.assigned_driver_phone = profile.phone
                else:
                    order.assigned_driver_phone = getattr(user, 'email', '')
            except Exception:
                order.assigned_driver_phone = getattr(user, 'email', '')
            order.save()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Notify owner and admin that order was received by driver
        try:
            from notifications.utils import notify_order_transition
            notify_order_transition(order, 'processing' if order.status == Order.Status.RECEIVED_BY_DRIVER else 'received', 'received_by_driver', kind='order_status')
        except Exception:
            pass

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, order_number=None):
        order = self.get_object()
        user = request.user
        if getattr(user, 'role', None) != 'driver':
            return Response({'detail': 'Only drivers can reject orders.'}, status=status.HTTP_403_FORBIDDEN)
        # Must be current dispatch driver if dispatching
        if order.dispatch_in_progress:
            queue = order.dispatch_queue or []
            if queue:
                expected_id = queue[order.dispatch_current_index % len(queue)] if queue else None
                if expected_id != user.id:
                    return Response({'detail': 'Not your turn to reject. Waiting for current driver.'}, status=status.HTTP_403_FORBIDDEN)
            # Trigger round-robin to next driver via Celery logic (synchronous fallback)
            try:
                from .tasks import handle_driver_timeout
                # Simulate timeout handling to move to next driver
                # Use current index
                current_idx = order.dispatch_current_index
                # Call the timeout handler synchronously (eager) or via task
                # For immediate reject, we directly advance
                next_idx = (current_idx + 1) % len(queue) if queue else 0
                next_driver_id = queue[next_idx] if queue else None
                if next_driver_id:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    try:
                        next_driver = User.objects.get(pk=next_driver_id)
                        order.dispatch_current_index = next_idx
                        order.driver = next_driver
                        order.save(update_fields=['dispatch_current_index', 'driver', 'updated_at'])
                        # Notify next driver
                        from notifications.models import Notification
                        Notification.objects.create(
                            user=next_driver,
                            order=order,
                            kind='assignment',
                            title=f'New Assignment: {order.order_number}',
                            message=f'You have a new order {order.order_number} from {order.origin} -> {order.destination}. Previous driver rejected. Tap Accept or Reject.',
                            stage_from='dispatching',
                            stage_to='dispatching',
                        )
                        # Also schedule timeout for next driver (skip in eager/test mode)
                        from django.conf import settings
                        if not getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
                            handle_driver_timeout.apply_async(args=[order.id, next_driver_id, next_idx], countdown=30)
                    except Exception as e:
                        logger.warning(f"Reject auto-routing failed: {e}")
                # Notify admin of reject + auto-route
                from django.contrib.auth import get_user_model
                User = get_user_model()
                for admin in User.objects.filter(role='admin'):
                    from notifications.models import Notification
                    Notification.objects.create(
                        user=admin,
                        order=order,
                        kind='assignment',
                        title=f'Driver rejected: {order.order_number}',
                        message=f'Driver {user.email} rejected {order.order_number}, auto-routed to next driver.',
                        stage_from='dispatching',
                        stage_to='dispatching',
                    )
                # Return current order state (still dispatching, next driver)
                order.refresh_from_db()
                serializer = self.get_serializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.warning(f"Reject handling failed for {order.order_number}: {e}")
                return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Fallback for non-dispatch orders (legacy)
        if order.driver_id != user.id:
            if order.driver_id is None and order.status in (Order.Status.PROCESSING, Order.Status.RECEIVED):
                return Response(self.get_serializer(order).data, status=status.HTTP_200_OK)
            return Response({'detail': 'Order not assigned to you.'}, status=status.HTTP_403_FORBIDDEN)
        if order.status not in [Order.Status.RECEIVED, Order.Status.PICKED_UP, Order.Status.PROCESSING]:
            return Response(
                {'detail': f'Cannot reject order in status {order.get_status_display()}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Unassign and return to pool
        order.driver = None
        if order.status == Order.Status.PICKED_UP:
            order.status = Order.Status.RECEIVED
        order.dispatch_in_progress = False
        order.dispatch_status = Order.DispatchStatus.IDLE
        try:
            order.save()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
