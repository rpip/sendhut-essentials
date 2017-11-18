from django.contrib import admin
from sendhut.lunch.models import (
    Partner, Menu, Item, SideMenu, SideItem,
    Image, ItemImage
)


admin.site.register(Partner)

admin.site.register(Menu)

admin.site.register(Item)

admin.site.register(SideMenu)

admin.site.register(SideItem)

admin.site.register(Image)

admin.site.register(ItemImage)
