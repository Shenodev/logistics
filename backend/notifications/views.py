import json
import time

from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    """GET /api/notifications/ — paginated list for current user, newest first."""
    qs = Notification.objects.filter(user=request.user).select_related('order').order_by('-created_at')
    # Simple limit param
    try:
        limit = int(request.query_params.get('limit', '20'))
        limit = max(1, min(limit, 100))
    except ValueError:
        limit = 20
    # Optional unread filter
    if request.query_params.get('unread') == 'true':
        qs = qs.filter(is_read=False)
    data = NotificationSerializer(qs[:limit], many=True).data
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'results': data, 'unread_count': unread_count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_read(request, pk=None):
    """POST /api/notifications/{id}/read/ — mark single as read."""
    try:
        n = Notification.objects.get(pk=pk, user=request.user)
    except Notification.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    n.is_read = True
    n.save(update_fields=['is_read'])
    return Response({'detail': 'Marked read.', 'id': n.id})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """POST /api/notifications/read-all/ — mark all as read."""
    updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'detail': f'Marked {updated} notifications read.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stream_notifications(request):
    """
    SSE endpoint: GET /api/notifications/stream/
    Streams text/event-stream with live order transition alerts.
    Uses DB polling (1.5s) for simplicity — no Redis required.
    Auth via HttpOnly JWT cookie (SessionCookieJWTAuthentication).
    """
    user = request.user
    # Parse Last-Event-ID for resume
    last_id = request.headers.get('Last-Event-ID') or request.GET.get('last_id') or '0'
    try:
        last_id_int = int(str(last_id).strip() or 0)
    except ValueError:
        last_id_int = 0

    def event_stream():
        nonlocal last_id_int
        # Send retry hint
        yield 'retry: 3000\n\n'
        # Initial heartbeat
        yield f': connected user={user.id}\n\n'
        # Poll loop — keep connection open ~45s, then client reconnects (EventSource auto)
        # For serverless, we limit duration; for local, we loop longer
        start = time.time()
        max_duration = 45  # seconds, client will reconnect
        while time.time() - start < max_duration:
            # Check for new notifications since last_id
            qs = Notification.objects.filter(user=user, id__gt=last_id_int).order_by('id')[:10]
            has = False
            for n in qs:
                has = True
                payload = {
                    'id': n.id,
                    'kind': n.kind,
                    'title': n.title,
                    'message': n.message,
                    'stage_from': n.stage_from,
                    'stage_to': n.stage_to,
                    'order_number': getattr(n.order, 'order_number', None),
                    'is_read': n.is_read,
                    'created_at': n.created_at.isoformat(),
                }
                # SSE format
                yield f'id: {n.id}\n'
                yield f'event: notification\n'
                yield f'data: {json.dumps(payload)}\n\n'
                last_id_int = n.id
            if not has:
                # Heartbeat to keep connection alive
                yield ': heartbeat\n\n'
            # Poll interval
            time.sleep(1.5)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    response['Access-Control-Allow-Credentials'] = 'true'
    # Ensure CORS for EventSource (browsers send no Origin header for SSE, but allow)
    return response
