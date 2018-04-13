from django.contrib import admin

from sendhut.db import BaseModelAdmin
from .models import Order, OrderLine


class OrderLineInline(admin.TabularInline):

    model = OrderLine
    exclude = ('metadata', 'deleted', 'data')
    raw_id_fields = ['item']
    extra = 0
    readonly_fields = ('store', 'special_instructions')

    def special_instructions(self, obj):
        return obj.special_instructions


@admin.register(Order)
class OrderAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'user',
        'delivery_time',
        'address',
        'notes',
        'reference',
        'group_order',
        'payment_reference',
    )
    list_filter = (
        'created',
        'time_window_start',
        'time_window_end',
        'address'
    )
    readonly_fields = ('group_order',)
    search_fields = ('reference',)
    inlines = [OrderLineInline]
