from random import choice

from django import template
from django.utils.text import slugify
from sendhut.lunch.models import Item

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


@register.filter(name='avg_delivery_time')
def avg_delivery_time(partner):
    # TODO(yao): calculate avg delivery time
    _min, _max = choice([(20, 30), (15, 25), (30, 40), (25, 35), (55, 65)])
    return '{} - {} Min'.format(_min, _max)
