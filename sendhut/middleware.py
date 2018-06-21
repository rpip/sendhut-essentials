from django.contrib.sites.models import Site

from sendhut.cart.utils import get_or_create_cart_from_request, set_cart_cookie
from sendhut.grouporder.utils import get_group_member_from_request
from sendhut.giveaways.utils import get_coupon_from_request


def site(get_response):
    """Clear the Sites cache and assign the current site to `request.site`.
    By default django.contrib.sites caches Site instances at the module
    level. This leads to problems when updating Site instances, as it's
    required to restart all application servers in order to invalidate
    the cache. Using this middleware solves this problem.
    """
    def middleware(request):
        Site.objects.clear_cache()
        request.site = Site.objects.get_current()
        return get_response(request)

    return middleware


def coupon(get_response):
    """Set's current giveaway and related coupon"""
    def middleware(request):
        request.coupon = get_coupon_from_request(request)
        return get_response(request)

    return middleware


def cart(get_response):
    """
    Get or create cart. Ensure views always receive a saved cart instance
    Also ensure matching views receive current group order
    """
    def middleware(request):
        cart = get_or_create_cart_from_request(request)
        member = get_group_member_from_request(request)
        if member:
            request.group_member = member
            request.cart = member.cart
        else:
            request.group_member = None
            request.cart = cart

        response = get_response(request)
        if not request.user.is_authenticated():
            set_cart_cookie(cart, response)

        return response

    return middleware
