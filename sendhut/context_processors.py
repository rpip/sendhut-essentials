from sendhut.lunch.models import FOOD_TAGS
from .cart import Cart


def cart(request):
    return {
        'cart': Cart(request),
        'food_tags': FOOD_TAGS
    }
