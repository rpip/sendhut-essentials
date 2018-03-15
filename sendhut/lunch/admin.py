# -*- coding: utf-8 -*-
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from safedelete.admin import SafeDeleteAdmin, highlight_deleted
from sorl.thumbnail.admin import AdminImageMixin

from .models import (
    Vendor, Menu, Item, Image,
    ItemImage, OptionGroup, Option, Order, OrderLine
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

    def toggle_display(modeladmin, request, queryset):
        for x in queryset:
            x.display = not(x.display)
            x.save()

    toggle_display.short_description = "Toggle the visibility of selected vendors"

    list_display = (
        'id',
        'created',
        'name',
        'address',
        'phone',
        'verified',
        'display'
    )
    list_filter = ('created', 'verified')
    search_fields = ('name',)
    actions = [toggle_display]


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


from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.forms import ModelForm
from sorl.thumbnail import get_thumbnail


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            t = get_thumbnail(value, "585x312", crop="center")
            output.append('<img src="{}">'.format(t.url))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


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
        'thumbnail',
        'is_primary',
    )
    list_filter = ('created', 'is_primary')
    form = ImageForm

    def thumbnail(self, obj):
        t = get_thumbnail(obj.image, "370x160", crop="center")
        return mark_safe('<img src="{}">'.format(t.url))

    thumbnail.short_description = 'Thumbnail'


class AdminItemImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value:
            img = Image.objects.get(id=value).image if isinstance(value, int) else value
            t = get_thumbnail(img, "585x312", crop="center")
            output.append('<img src="{}">'.format(t.url))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class ItemImageForm(ModelForm):
    class Meta:
        model = ItemImage
        fields = ('image',)
        widgets = {
            'image': AdminItemImageWidget
        }


class ImageInlineFormset(BaseInlineFormSet):

    def clean(self):
        # errors: image required, image not part of choices
        import pdb; pdb.set_trace()

    def save_new(self, form, commit=True):
        # return super().save_new(form, commit=commit)
        import pdb; pdb.set_trace()

    def save_existing(self, form, instance, commit=True):
        #return form.save(commit=commit)
        import pdb; pdb.set_trace()


class ImageInlineModelAdmin(AdminImageMixin, admin.TabularInline):
    model = Item.images.through
    exclude = ('deleted', 'created', 'metadata')
    extra = 0
    form = ItemImageForm
    formset = ImageInlineFormset


@admin.register(Item)
class ItemAdmin(BaseModelAdmin):
    # TODO(yao): limit menu filter to store menu
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
        'toppings',
        'variants',
    )
    list_filter = ('created', 'available')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ['name']}
    inlines = [ImageInlineModelAdmin]
    exclude = ('deleted', 'created', 'metadata')

    def toppings(self, obj):
        return bool(obj.metadata.get('options'))

    toppings.boolean = True

    def variants(self, obj):
        return bool(obj.metadata.get('variants'))

    variants.boolean = True

    def save_formset(self, request, form, formset, change):
        import pdb; pdb.set_trace()
        instances = formset.save(commit=False)
        for instance in instances:
            # Do something with `instance`
            instance.save()
            # instance.item.update_totals()

        formset.save_m2m()

    #def save_related(self, request, form, formsets, change):


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
