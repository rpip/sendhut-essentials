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
        'state',
        'cart',
        'code',
        'status',
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
        'status',
        'redeemed_at'
    )


@admin.register(GiveAway)
class GiveAwayAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'token',
        'status',
        'name',
        'description',
        'created_by',
        'valid_until',
        'discount_value_currency',
        'discount_value',
        'num_coupons',
        'num_coupons_used',
        'num_coupons_unused',
        'num_coupons_expired'
    )
    list_filter = ('created_by', 'created', 'valid_until')
    search_fields = ('name', 'description', )
    inlines = [CouponInline]

    def num_coupons(self, obj):
        return obj.coupons.count()
    num_coupons.short_description = "coupons"

    def num_coupons_used(self, obj):
        return obj.coupons.used().count()
    num_coupons_used.short_description = "used"

    def num_coupons_unused(self, obj):
        return obj.coupons.used().count()
    num_coupons_unused.short_description = "unused"

    def num_coupons_expired(self, obj):
        return obj.coupons.expired().count()
    num_coupons_expired.short_description = "expired"


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
