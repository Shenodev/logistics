from django.contrib import admin
from django.urls import include, path

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health),
    path('auth/', include('accounts.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/v1/refunds/', include('invoices.urls')),
    path('api/v1/refunds', include('invoices.urls')),
    path('api/notifications/', include('notifications.urls')),
]