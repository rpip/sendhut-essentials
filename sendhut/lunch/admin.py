# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Partner, Menu, Item, Image, ItemImage, OptionGroup, Option, Order, OrderItem


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'address',
        'phone',
        'location',
    )
    list_filter = ('created',)
    search_fields = ('name',)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'partner',
        'label',
    )
    list_filter = ('created',)
    search_fields = ('name',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
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
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'image',
        'thumbnail_path',
        'is_primary',
    )
    list_filter = ('created', 'is_primary')


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'item',
        'image',
    )
    list_filter = ('created',)
    raw_id_fields = ('item', 'image')


@admin.register(OptionGroup)
class OptionGroupAdmin(admin.ModelAdmin):
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
class OptionAdmin(admin.ModelAdmin):
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


class OrderItemInline(admin.TabularInline):

    model = OrderItem
    raw_id_fields = ['item', 'options']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'user',
        'reference',
        'delivery_date',
        'delivery_address',
        'special_instructions',
        'paid',
    )
    list_filter = (
        'created',
        'user',
        'delivery_date',
        'delivery_address',
        'paid',
    )
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
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
    raw_id_fields = ('options',)
