from django.contrib import admin
from sendhut.db import BaseModelAdmin

from .models import GroupOrder, Member


class GroupOrderInline(admin.StackedInline):

    model = Member
    exclude = ('metadata',)
    raw_id_fields = ['cart']
    extra = 0


@admin.register(GroupOrder)
class GroupCartAdmin(BaseModelAdmin):
    list_display = [
        'user',
        'store',
        'monetary_limit',
        'created'
    ]
    inlines = [GroupOrderInline]
