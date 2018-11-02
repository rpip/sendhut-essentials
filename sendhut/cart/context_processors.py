"""Cart-related context processors."""
from .utils import get_cart_from_request


def cart(request):
    """Inject cart in context"""
    return {'cart': get_cart_from_request(request)}
