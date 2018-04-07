"""Cart-related context processors."""
from .utils import get_cart_from_request


def cart(request):
    """Inject cart in context"""
    cart = get_cart_from_request(request)
    return {'cart': cart}
