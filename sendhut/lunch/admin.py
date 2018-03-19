# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.forms import ModelForm

from safedelete.admin import SafeDeleteAdmin, highlight_deleted
from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail import get_thumbnail

from .models import (
    Store, Menu, Item, ItemVariant, Image,
    OptionGroup, Option, Order, OrderLine, GroupCart,
    GroupCartMember
)


def thumbnail(obj):
    if obj.image:
        img = obj.image if isinstance(obj, Image) else obj.image.image
        if img:
            t = get_thumbnail(img, "128x128", crop="center")
            return mark_safe('<img src="{}">'.format(t.url))
    return None


thumbnail.short_description = 'Image'


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            t = get_thumbnail(value, "585x312", crop="center")
            output.append('<img src="{}">'.format(t.url))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class BaseModelAdmin(SafeDeleteAdmin):

    exclude = ('metadata',)
    _list_display = (highlight_deleted,) + SafeDeleteAdmin.list_display
    _list_filter = SafeDeleteAdmin.list_filter

    def get_list_display(self, request):
        return tuple(self.list_display) + self._list_display

    def get_list_filter(self, request):
        return tuple(self.list_filter) + self._list_filter


@admin.register(Store)
class StoreAdmin(BaseModelAdmin):

    def toggle_display(modeladmin, request, queryset):
        for x in queryset:
            x.display = not(x.display)
            x.save()

    toggle_display.short_description = "Toggle the visibility of selected stores"

    list_display = (
        'id',
        'created',
        'name',
        'address',
        'phone',
        'get_banner_img',
        'verified',
        'display'
    )
    list_filter = ('created', 'verified')
    search_fields = ('name',)
    actions = [toggle_display]
    raw_id_fields = ('banner', 'logo')

    def get_banner_img(self, obj):
        t = get_thumbnail(obj.banner.image, "128x128", crop="center")
        return mark_safe('<img src="{}">'.format(t.url))


@admin.register(Menu)
class MenuAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'store'
    )
    list_filter = ('created',)
    search_fields = ('name',)


class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ('image',)
        widgets = {
            'image': AdminImageWidget,
        }


@admin.register(Image)
class ImageAdmin(BaseModelAdmin, AdminImageMixin):
    list_display = (
        'id',
        'created',
        thumbnail
    )
    list_filter = ('created',)
    form = ImageForm


class ItemVariantInline(admin.TabularInline):

    model = ItemVariant
    exclude = ('metadata', 'deleted', 'price_currency')
    raw_id_fields = ['item']
    extra = 0
    form = ImageForm


class VariantsListFilter(admin.SimpleListFilter):
    title = _('has variants')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'variants'

    def lookups(self, request, model_admin):
        return (
            (1, _('Has variants')),
            (0, _('No variants')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if bool(int(self.value())):
                return Item.objects.filter(variants__isnull=False)

            return Item.objects.filter(variants__isnull=True)


class ToppingsListFilter(admin.SimpleListFilter):
    title = _('has toppings')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'toppings'

    def lookups(self, request, model_admin):
        return (
            (1, _('Has toppings')),
            (0, _('No toppings')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if bool(int(self.value())):
                return Item.objects.filter(option_groups__isnull=False)

            return Item.objects.filter(options_group__isnull=True)


@admin.register(Item)
class ItemAdmin(BaseModelAdmin):
    # TODO(yao): limit menu filter to store menu
    list_display = (
        'id',
        'name',
        'categories',
        'menu',
        'description',
        'price',
        thumbnail,
        'dietary_labels',
        'available',
        'toppings',
        'variants'
    )
    list_filter = (
        'created',
        'available',
        VariantsListFilter,
        ToppingsListFilter
    )
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ['name']}
    exclude = ('deleted', 'created', 'metadata')
    raw_id_fields = ('image',)
    inlines = [ItemVariantInline]

    def toppings(self, obj):
        return bool(obj.metadata.get('options'))

    toppings.boolean = True

    def variants(self, obj):
        return obj.variants.count() > 0

    variants.boolean = True


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


class GroupCartInline(admin.StackedInline):

    model = GroupCartMember
    exclude = ('metadata',)
    raw_id_fields = ['group_cart']
    extra = 0


@admin.register(GroupCart)
class GroupCartAdmin(BaseModelAdmin):
    list_display = [
        'owner',
        'store',
        'monetary_limit',
        'created'
    ]
    inlines = [GroupCartInline]
