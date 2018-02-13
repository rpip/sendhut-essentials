from django.contrib import admin
from .models import Merchant


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'email',
        'phone_number',
        'business_name'
    )
    list_filter = ('created',)
    search_fields = ('name', 'email', 'phone', 'business_name')
