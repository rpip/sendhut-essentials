from sendhut.lunch.models import FOOD_TAGS, Order
from sendhut.lunch.views import GroupOrder
from sendhut import utils
from .cart import Cart


def cart(request):
    group_session = GroupOrder.get(request)
    return {
        'cart': Cart(request),
        'food_tags': FOOD_TAGS,
        'delivery_schedule': Order.DELIVERY_TIMES,
        'group_session': group_session,
        'is_mobile': utils.is_mobile(request)
    }
