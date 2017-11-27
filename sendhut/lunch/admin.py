from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin
# from sorl.thumbnail.admin import AdminImageMixin
from sendhut.lunch.models import (
    Partner, Menu, Item, SideMenu, SideItem,
    Image, ItemImage
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
