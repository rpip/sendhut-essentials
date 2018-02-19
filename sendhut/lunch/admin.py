# -*- coding: utf-8 -*-
from django.contrib import admin

from safedelete.admin import SafeDeleteAdmin, highlight_deleted

from .models import (
    Vendor, Menu, Item, Image,
    ItemImage, OptionGroup, Option, Order, OrderLine,
    GroupCart
)


class BaseModelAdmin(SafeDeleteAdmin):

    exclude = ('metadata',)
    _list_display = (highlight_deleted,) + SafeDeleteAdmin.list_display
    _list_filter = SafeDeleteAdmin.list_filter

    def get_list_display(self, request):
        return tuple(self.list_display) + self._list_display

    def get_list_filter(self, request):
        return tuple(self.list_filter) + self._list_filter


@admin.register(Vendor)
class VendorAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'address',
        'phone',
        'verified',
    )
    list_filter = ('created', 'verified')
    search_fields = ('name',)


@admin.register(Menu)
class MenuAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'vendor'
    )
    list_filter = ('created',)
    search_fields = ('name',)


@admin.register(Item)
class ItemAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'categories',
        'menu',
        'name',
        'slug',
        'description',
        'price_currency',
        'price',
        'dietary_labels',
        'available',
    )
    list_filter = ('created', 'available')
    raw_id_fields = ('menu',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ['name']}


@admin.register(Image)
class ImageAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'image',
        'thumbnail_path',
        'is_primary',
    )
    list_filter = ('created', 'is_primary')


@admin.register(ItemImage)
class ItemImageAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'item',
        'image',
    )
    list_filter = ('created',)
    raw_id_fields = ('item', 'image')


@admin.register(OptionGroup)
class OptionGroupAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'item',
        'is_required',
        'multi_select',
    )
    list_filter = (
        'created',
        'is_required',
        'multi_select',
    )
    raw_id_fields = ('item',)
    search_fields = ('name',)


@admin.register(Option)
class OptionAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'price_currency',
        'price',
        'group',
    )
    list_filter = ('created',)
    raw_id_fields = ('group',)
    search_fields = ('name',)


class OrderLineInline(admin.TabularInline):

    model = OrderLine
    exclude = ('metadata',)
    raw_id_fields = ['item']


@admin.register(Order)
class OrderAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'user',
        'reference',
        'delivery_time',
        'delivery_address',
        'notes',
        'payment'
    )
    list_filter = (
        'created',
        'delivery_time',
        'delivery_address'
    )
    search_fields = ('reference',)
    inlines = [OrderLineInline]


@admin.register(OrderLine)
class OrderLineAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'item',
        'quantity',
        'price_currency',
        'price',
        'special_instructions',
        'order',
    )
    list_filter = ('created', 'item', 'order')


class GroupOrderInline(admin.StackedInline):

    model = Order
    exclude = ('metadata',)
    raw_id_fields = ['group_cart']
    extra = 0


# @admin.register(GroupCart)
# class GroupCartAdmin(BaseModelAdmin):
#     list_display = [
#         'owner',
#         'vendor',
#         'monetary_limit',
#         'created'
#     ]
#     inlines = [GroupOrderInline]
