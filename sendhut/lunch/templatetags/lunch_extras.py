from random import choice

from djmoney.money import Money
from django import template
from django.utils.text import slugify
from django.conf import settings

from sendhut.lunch.models import Item
from sendhut.utils import unslugify

register = template.Library()


@register.filter(name='dietary_label')
def dietary_label(label_id):
    return Item.dietary_label_text(label_id)


@register.filter(name='dietary_label_short')
def dietary_labels(label):
    label = slugify(label)
    if label == 'vegan':
        return 'VG'
    elif label == 'vegetarian':
        return 'V'
    elif label == 'halal':
        return 'H'
    elif label == 'gluten-free':
        return 'GF'
    elif label == 'dairy-free':
        return 'DF'


@register.filter(name='subcart_total')
def subcart_total(cart):
    total = sum(float(x['data']['total']) for x in cart)
    return Money(total, 'NGN')


@register.filter(name='times')
def times(n):
    return range(n)


@register.filter(name='group_cart_limit')
def group_cart_limit(group_cart):
    if group_cart.monetary_limit:
        return "Limit {} per person".format(group_cart.monetary_limit)


@register.filter(name='unslugify')
def _unslugify(text):
    return unslugify(text)
