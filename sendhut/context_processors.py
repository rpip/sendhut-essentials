from django.conf import settings
from sendhut.lunch.models import FOOD_TAGS, Order
from .cart import Cart


def cart(request):
    return {
        'cart': Cart(request),
        'food_tags': FOOD_TAGS,
        'delivery_schedule': Order.DELIVERY_TIMES,
        'group_order_session': request.session.get(settings.GROUP_CART_SESSION_ID)
    }
