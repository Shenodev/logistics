from django.contrib import admin

from .models import DriverProfile


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'vehicle_plate', 'vehicle_type', 'availability', 'is_available', 'rating', 'current_orders_count', 'max_orders')
    list_filter = ('availability', 'is_available', 'vehicle_type')
    search_fields = ('user__email', 'license_number', 'vehicle_plate', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user',)
