from django.contrib import admin
from django.utils.html import format_html, mark_safe, format_html_join

from sendhut.db import BaseModelAdmin
from .models import GroupOrder, Member


class MemberInline(admin.StackedInline):

    model = Member
    exclude = ('metadata', 'deleted', 'name', 'state')
    raw_id_fields = ['cart']
    readonly_fields = ('member_name', 'items')
    extra = 0

    def member_name(self, obj):
        return obj.get_name()

    def items(self, obj):
        table = """
          <table class="table table-striped">
            <thead>
              <tr>
                <th scope="col">Item</th>
                <th scope="col">Quantity</th>
                <th scope="col">Price</th>
                <th scope="col">Special instructions</th>
              </tr>
            </thead>
            <tbody>
              {}
            </tbody>
           </table>
        """
        row_tpl = """
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
        </tr>
        """
        rows = format_html_join(
            '', row_tpl, (
                (x.item.name, x.quantity, x.item.price, x.data.get('notes'))
                for x in obj.cart.lines.all())
        )
        return format_html(table, rows)

    items.allow_tags = True
    items.short_description = "Cart Items"


@admin.register(GroupOrder)
class GroupOrderAdmin(BaseModelAdmin):

    list_display = [
        'user',
        'store',
        'monetary_limit',
        'total',
        'status',
        'created'
    ]

    exclude = ('deleted',)
    readonly_fields = ('total', 'status')
    list_filter = ('status', 'created')
    inlines = [MemberInline]

    def total(self, obj):
        return obj.get_total()
