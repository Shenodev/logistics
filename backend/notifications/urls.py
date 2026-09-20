from django.urls import path

from .views import list_notifications, mark_all_read, mark_read, stream_notifications

urlpatterns = [
    path('', list_notifications, name='notifications-list'),
    path('stream/', stream_notifications, name='notifications-stream'),
    path('read-all/', mark_all_read, name='notifications-read-all'),
    path('<int:pk>/read/', mark_read, name='notifications-read'),
]
