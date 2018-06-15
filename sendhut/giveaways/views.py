from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Coupon
from .utils import set_coupon_cookie


@login_required
def join_giveaway(request, code):
    coupon = get_object_or_404(Coupon, code=code)
    response = redirect('home')
    set_coupon_cookie(coupon, response)
    return response


@login_required
def leave_giveaway(request, code):
    return redirect('home')


@login_required
def giveaway_list(request):
    pass
