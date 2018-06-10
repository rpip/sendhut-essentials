from django.contrib import admin

from sendhut.db import BaseModelAdmin
from .models import Order, OrderLine


class OrderLineInline(admin.TabularInline):

    model = OrderLine
    exclude = ('metadata', 'deleted', 'data')
    raw_id_fields = ['item']
    extra = 0
    readonly_fields = ('store', 'special_instructions')

    def special_instructions(self, obj):
        return obj.special_instructions


@admin.register(Order)
class OrderAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'created',
        'user',
        'delivery_time',
        #'address',
        'notes',
        'reference',
        'group_order_link',
        'payment_reference',
    )
    list_filter = (
        'created',
        'time_window_start',
        'time_window_end',
        #'address'
    )

    def group_order_link(self, obj):
        from sendhut.grouporder.models import GroupOrder
        if not obj.group_order:
            return ''

        grouporder = GroupOrder.objects.get(token=obj.group_order)
        return u'<a href="/admin/grouporder/grouporder/%s/">%s</a>' % (grouporder.id, grouporder.token)

    group_order_link.allow_tags = True
    group_order_link.short_description = "group order link"

    def user_info(self, obj):
        fullname = obj.user.get_full_name()
        email = obj.user.email
        phone = obj.user.phone
        return '{} - {} - {}'.format(fullname, phone, email)

    user_info.allow_tags = True

    readonly_fields = ('group_order', 'user_info')
    search_fields = ('reference',)
    inlines = [OrderLineInline]
