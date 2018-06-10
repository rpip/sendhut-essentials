# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Coupon, Campaign, CampaignDropoff


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'updated',
        'deleted',
        'metadata',
        'uuid',
        'code',
        'value_currency',
        'value',
        'user',
        'status',
        'campaign',
        'redeemed_at',
    )
    list_filter = (
        'created',
        'updated',
        'deleted',
        'user',
        'campaign',
        'redeemed_at',
    )


class CouponInline(admin.TabularInline):

    model = Coupon
    exclude = ('metadata', 'deleted', 'value')
    extra = 0
    readonly_fields = (
        'campaign',
        'monetary_value',
        'code',
        'user',
        'status',
        'redeemed_at'
    )

    def has_add_permission(self, request):
        return False


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    exclude = ('metadata', 'deleted')
    list_display = (
        'id',
        'name',
        'description',
        'created_by',
        'user_limit',
        'value_currency',
        'value',
        'valid_until',
        'is_expired',
        'num_coupons',
        'num_coupons_used',
        'num_coupons_unused',
        'num_coupons_expired'
    )
    list_filter = ('created_by', 'valid_until')
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


@admin.register(CampaignDropoff)
class CampaignDropoffAdmin(admin.ModelAdmin):
    exclude = ('metadata', 'deleted')
    list_display = (
        'id',
        'created',
        'campaign',
        'address',
    )
    list_filter = ('created', 'campaign', 'address')
