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
        'reference',
        'time',
        'address',
        'notes',
    )
    list_filter = (
        'created',
        'time',
        'address'
    )
    search_fields = ('reference',)
    inlines = [OrderLineInline]
