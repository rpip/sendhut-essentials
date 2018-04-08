from django import template

from sendhut.grouporder.utils import get_group_share_url


register = template.Library()


@register.simple_tag(takes_context=True)
def shareable_link(context, group_order):
    request = context['request']
    return get_group_share_url(request, group_order)
