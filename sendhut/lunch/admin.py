from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin
# from sorl.thumbnail.admin import AdminImageMixin
from .models import (
    Partner, Menu, Item, SideMenu, SideItem,
    Image, ItemImage, Order, Order, OrderItem
)


class ImageAdmin(AdminImageMixin, admin.ModelAdmin):
    pass


admin.site.register(Partner)

admin.site.register(Menu)

admin.site.register(Item)

admin.site.register(SideMenu)

admin.site.register(SideItem)

admin.site.register(ItemImage)

admin.site.register(Image, ImageAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['item']


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'delivery_address',
        'delivery_date',
        'reference',
        'special_instructions',
        'paid',
        'created',
        'updated'
    ]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)
