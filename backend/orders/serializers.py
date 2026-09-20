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
            'customer_phone', 'restaurant_name', 'restaurant_address',
            'delivery_status', 'delivery_updated_at',
            'cancelled_at', 'cancelled_by', 'refund_status', 'refund_id', 'invoice_id', 'stripe_payment_intent_id',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'owner', 'cancelled_at', 'cancelled_by',
            'refund_status', 'refund_id', 'invoice_id', 'stripe_payment_intent_id',
            'created_at', 'updated_at', 'status_display',
            'owner_email', 'driver_email',
        ]

    def validate_status(self, value):
        # Normalize legacy aliases
        mapped = Order.LEGACY_STATUS_MAP.get(value, value)
        if mapped not in dict(Order.Status.choices):
            raise serializers.ValidationError(f'Invalid status {value}')
        return mapped

    def validate_delivery_status(self, value):
        allowed = {'assigned', 'picked_up', 'on_the_way', 'delivered'}
        if value not in allowed:
            raise serializers.ValidationError(f'Invalid delivery_status {value}')
        return value

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
        delivery_status = attrs.get('delivery_status')
        if self.instance and delivery_status and delivery_status != self.instance.delivery_status:
            if not self.instance.can_transition_delivery(delivery_status):
                allowed = ', '.join(sorted(self.instance.DELIVERY_ALLOWED.get(self.instance.delivery_status, set()))) or 'none'
                raise serializers.ValidationError({
                    'delivery_status': f'Invalid delivery transition {self.instance.delivery_status} -> {delivery_status}. Allowed: {allowed}'
                })
        return attrs
