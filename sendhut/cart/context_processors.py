"""Cart-related context processors."""
from .utils import get_cart_from_request


def cart(request):
    """Expose the number of items in cart."""
    cart = get_cart_from_request(request)
    return {'cart': cart}
