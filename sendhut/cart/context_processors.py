"""Cart-related context processors."""
from .utils import get_cart_from_request


def cart(request):
    """Inject cart in context"""
    cart = get_cart_from_request(request)
    # if request.coupon:
    #     stores = request.coupon.stores
    #     cart = [x for x in cart.lines.all() if
    #             x.item.store in stores]
    # TODO(yao): filter out on stuff from giveaway stores
    return {'cart': cart}
