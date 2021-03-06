# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.html import format_html, mark_safe, format_html_join
from django.shortcuts import get_object_or_404
from django.forms import ModelForm

from sorl.thumbnail import get_thumbnail
from multiupload.admin import MultiUploadAdmin

from sendhut.db import BaseModelAdmin
from .models import (
    Store, Menu, Item, ItemVariant, Image, OptionGroup, Option
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


class MenuInline(admin.StackedInline):

    model = Menu
    exclude = ('metadata', 'deleted')
    readonly_fields = ('edit_link',)
    extra = 0

    def edit_link(self, obj):
        return mark_safe('<a href="{}">Edit Menu</a>'.format(obj.get_admin_url()))

    edit_link.allow_tags = True


@admin.register(Store)
class StoreAdmin(BaseModelAdmin):

    def toggle_display(self, request, queryset):
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
    list_filter = ('created', 'display')
    search_fields = ('name', 'address', 'phone')
    actions = [toggle_display]
    raw_id_fields = ('banner', 'logo')
    inlines = [MenuInline]

    def get_banner_img(self, obj):
        if obj.banner:
            t = get_thumbnail(obj.banner.image, "128x128", crop="center")
            return mark_safe('<img src="{}">'.format(t.url))


class ItemInline(admin.StackedInline):

    model = Item
    exclude = ('metadata', 'deleted', 'slug', 'price_currency',)
    extra = 0


@admin.register(Menu)
class MenuAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'name',
        'store'
    )
    list_filter = ('created',)
    search_fields = ('name', 'store__name')
    readonly_fields = ('related_menus',)
    inlines = [ItemInline]

    def related_menus(self, obj):
        ul = "<ul>{}</ul>"
        li = "<li><a href='{}'>{}</a></li>"
        other_menus = [x for x in obj.store.menus.all() if x.id != obj.id]
        menus = format_html_join(
            '', li, (
                (x.get_admin_url(), x.name)
                for x in other_menus)
        )
        return format_html(ul, menus)

    related_menus.allow_tags = True


class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ('image',)
        widgets = {
            'image': AdminImageWidget,
        }


@admin.register(Image)
class ImageAdmin(BaseModelAdmin, MultiUploadAdmin):
    list_display = (
        'id',
        'created',
        thumbnail
    )
    list_filter = ('created',)
    form = ImageForm
    change_form_template = 'multiupload/change_form.html'
    change_list_template = 'multiupload/change_list.html'
    multiupload_template = 'multiupload/upload.html'
    multiupload_list = True
    multiupload_form = True
    # min allowed filesize for uploads in bytes
    multiupload_minfilesize = 0
    # tuple with mimetype accepted
    multiupload_acceptedformats = ("image/jpeg", "image/pjpeg", "image/png",)

    def process_uploaded_file(self, uploaded, object, request):
        f = self.model.objects.create(image=uploaded)
        return {
            'url': f.thumb_lg().url,
            'thumbnail_url': f.thumb_sm().url,
            'id': f.id,
            'name': f.image.name
        }

    def delete_file(self, pk, request):
        obj = get_object_or_404(self.queryset(request), pk=pk)
        obj.delete()


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
    # TODO(yao): inline options
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
