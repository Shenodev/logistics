from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_number'
    lookup_url_kwarg = 'order_number'

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related('owner', 'driver', 'cancelled_by').all()
        # Role-aware filtering
        if getattr(user, 'role', None) == 'admin' or getattr(user, 'is_staff', False):
            return qs
        if getattr(user, 'role', None) == 'driver':
            # Drivers see unassigned pool (received, no driver) + their assigned orders
            return qs.filter(Q(driver=user) | Q(status='received', driver__isnull=True))
        # Regular users see only their own orders
        return qs.filter(owner=user)

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

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, order_number=None):
        order = self.get_object()
        # Strict Stage 1 check — must be exactly Received
        if order.status != Order.Status.RECEIVED:
            return Response(
                {'detail': f'Only orders in Stage 1 (Received) can be cancelled. Current status is {order.get_status_display()}.',
                 'status': order.status},
                status=status.HTTP_400_BAD_REQUEST,
            )
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
        try:
            order.save()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, order_number=None):
        order = self.get_object()
        user = request.user
        if getattr(user, 'role', None) != 'driver':
            return Response({'detail': 'Only drivers can accept orders.'}, status=status.HTTP_403_FORBIDDEN)
        if order.status != Order.Status.RECEIVED:
            return Response(
                {'detail': f'Only orders in Stage 1 (Received) can be accepted. Current status is {order.get_status_display()}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if order.driver_id and order.driver_id != user.id:
            return Response({'detail': 'Order already assigned to another driver.'}, status=status.HTTP_409_CONFLICT)
        if order.driver_id == user.id and order.status == Order.Status.PICKED_UP:
            return Response({'detail': 'Order already accepted.'}, status=status.HTTP_400_BAD_REQUEST)

        # Assign and transition to picked_up
        order.driver = user
        order.status = Order.Status.PICKED_UP
        try:
            order.save()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, order_number=None):
        order = self.get_object()
        user = request.user
        if getattr(user, 'role', None) != 'driver':
            return Response({'detail': 'Only drivers can reject orders.'}, status=status.HTTP_403_FORBIDDEN)
        # Allow reject if order is assigned to this driver and still in early stage
        if order.driver_id != user.id:
            # Also allow rejecting an unassigned order from pool (no-op, just acknowledge)
            if order.driver_id is None and order.status == Order.Status.RECEIVED:
                return Response(self.get_serializer(order).data, status=status.HTTP_200_OK)
            return Response({'detail': 'Order not assigned to you.'}, status=status.HTTP_403_FORBIDDEN)
        if order.status not in [Order.Status.RECEIVED, Order.Status.PICKED_UP]:
            return Response(
                {'detail': f'Cannot reject order in status {order.get_status_display()}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Unassign and return to pool (received)
        order.driver = None
        # If it was picked_up, revert to received to allow re-dispatch
        if order.status == Order.Status.PICKED_UP:
            order.status = Order.Status.RECEIVED
        try:
            order.save()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
