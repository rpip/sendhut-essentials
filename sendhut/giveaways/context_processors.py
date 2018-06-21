"""Group order related context processors."""
from .utils import get_coupon_from_request


def coupon(request):
    """Inject group order info into context"""
    coupon = get_coupon_from_request(request)
    if coupon:
        return {'coupon': request.coupon}

    return {}
