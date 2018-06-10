from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Coupon
from .utils import redeem_coupon


@login_required
def claim_coupon(request, code):
    try:
        coupon = redeem_coupon(code, request.user)
    except Coupon.DoesNotExist:
        invalid_msg = "The coupon you are trying to redeem is not valid. Please check \
        for mistakes and try again"
        messages.error(request, invalid_msg)
    else:
        msg = "Coupon {} has been added to your account. Use this on \
        your next order at checkout".format(coupon.campaign)
        messages.info(request, msg)

    return redirect('home')
