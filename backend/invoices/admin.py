from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'user', 'order', 'amount', 'currency', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('invoice_number', 'user__email', 'order__order_number')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user', 'order')
