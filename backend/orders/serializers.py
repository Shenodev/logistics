from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    driver_email = serializers.EmailField(source='driver.email', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'owner', 'owner_email',
            'driver', 'driver_email',
            'status', 'status_display',
            'origin', 'origin_code', 'destination', 'destination_code',
            'mode', 'priority', 'gross_weight',
            'cancelled_at', 'cancelled_by', 'refund_status', 'refund_id', 'invoice_id',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'owner', 'cancelled_at', 'cancelled_by',
            'refund_status', 'refund_id', 'invoice_id',
            'created_at', 'updated_at', 'status_display',
            'owner_email', 'driver_email',
        ]

    def validate_status(self, value):
        # Normalize legacy aliases
        mapped = Order.LEGACY_STATUS_MAP.get(value, value)
        if mapped not in dict(Order.Status.choices):
            raise serializers.ValidationError(f'Invalid status {value}')
        return mapped

    def validate(self, attrs):
        # On update, enforce state-machine via model clean
        status = attrs.get('status')
        if self.instance and status and status != self.instance.status:
            # Use model logic to check transition
            tmp = self.instance
            # Temporarily set new status for can_transition check without saving
            if not tmp.can_transition(status):
                allowed = ', '.join(sorted(tmp.ALLOWED_TRANSITIONS.get(tmp.status, set()))) or 'none (terminal)'
                raise serializers.ValidationError({
                    'status': f'Invalid transition {tmp.get_status_display()} -> {dict(Order.Status.choices).get(status, status)}. Allowed: {allowed}'
                })
            if status == Order.Status.CANCELLED and tmp.status != Order.Status.RECEIVED:
                raise serializers.ValidationError({'status': 'Only orders in Stage 1 (Received) can be cancelled'})
        return attrs
