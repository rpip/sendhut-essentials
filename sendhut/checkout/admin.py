from django.contrib import admin

from sendhut.db import BaseModelAdmin
from .models import Order, OrderLine


class OrderLineInline(admin.TabularInline):

    model = OrderLine
    exclude = ('metadata',)
    raw_id_fields = ['item']
    extra = 0


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
