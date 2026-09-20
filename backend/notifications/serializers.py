from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True, allow_null=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'kind', 'title', 'message',
            'stage_from', 'stage_to',
            'order', 'order_number',
            'is_read', 'created_at', 'time_ago',
        ]
        read_only_fields = ['id', 'created_at', 'time_ago', 'order_number']

    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        if delta.total_seconds() < 60:
            return 'just now'
        return f'{timesince(obj.created_at, timezone.now()).split(",")[0]} ago'
