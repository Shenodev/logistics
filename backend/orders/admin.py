from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'owner', 'driver', 'status', 'refund_status', 'origin', 'destination', 'created_at')
    list_filter = ('status', 'refund_status', 'mode', 'priority')
    search_fields = ('order_number', 'owner__email', 'driver__email', 'origin', 'destination')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('owner', 'driver')
