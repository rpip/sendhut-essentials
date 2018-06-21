# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Coupon, GiveAway, GiveAwayDropoff, GiveAwayStore


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'redeemed_at',
        'user',
        'cart',
        'code',
        'giveaway',
    )
    list_filter = ('created', 'updated', 'deleted')


class CouponInline(admin.TabularInline):

    model = Coupon
    exclude = ('metadata', 'deleted', 'value')
    extra = 0
    readonly_fields = (
        'giveaway',
        'code',
        'user',
        'redeemed_at'
    )


class GiveAwayStoresInline(admin.TabularInline):

    model = GiveAwayStore
    extra = 0
    exclude = ('metadata', 'deleted', 'created')


class GiveAwayDropoffInline(admin.TabularInline):

    model = GiveAwayDropoff
    extra = 0
    exclude = ('metadata', 'deleted', 'created')
    readonly_fields = ('address',)


@admin.register(GiveAway)
class GiveAwayAdmin(admin.ModelAdmin):
    exclude = ('metadata', 'deleted', 'created')
    list_display = (
        'id',
        'created',
        'status',
        'name',
        'description',
        'created_by',
        'valid_until',
        'discount_value',
        'num_coupons',
        'num_coupons_redeemed',
        'num_coupons_unused',
        'total_order',
    )
    list_filter = ('created_by', 'created', 'valid_until')
    search_fields = ('name', 'description', )
    inlines = (
        CouponInline,
        GiveAwayStoresInline,
        GiveAwayDropoffInline
    )
    readonly_fields = ('total_order',)

    def total_order(self, obj):
        return obj.get_total()

    def num_coupons(self, obj):
        return obj.coupons.count()
    num_coupons.short_description = "coupons"

    def num_coupons_redeemed(self, obj):
        return obj.coupons.redeemed().count()
    num_coupons_redeemed.short_description = "redeemed"

    def num_coupons_unused(self, obj):
        return obj.coupons.unused().count()
    num_coupons_unused.short_description = "unused"


@admin.register(GiveAwayDropoff)
class GiveAwayDropoffAdmin(admin.ModelAdmin):
    list_display = (
        'giveaway',
        'address',
    )


@admin.register(GiveAwayStore)
class GiveAwayStoreAdmin(admin.ModelAdmin):
    list_display = (
        'giveaway',
        'store',
    )
