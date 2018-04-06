# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Cart, CartLine


class CartLineInline(admin.TabularInline):

    model = CartLine
    exclude = ('metadata', 'deleted', 'created')
    raw_id_fields = ['item']
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'updated',
        'status',
        'user',
        'token',
    )
    exclude = ('metadata', 'deleted', 'created')
    list_filter = ('user',)
    inlines = [CartLineInline]
