from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Coupon
from .utils import set_coupon_cookie, leave_giveaway_session


def join_giveaway(request, code):
    coupon = get_object_or_404(Coupon.objects.unused(), code=code)
    response = redirect('home')
    set_coupon_cookie(coupon, request, response)
    return response


def leave_giveaway(request, code):
    if request.user.is_authenticated():
        # delete coupon session cart. it's transient on login/logout
        request.cart.hard_delete()

    response = redirect('home')
    leave_giveaway_session(response)
    return response
