from datetime import datetime, timedelta
from django.http import Http404
from django.core.urlresolvers import resolve
from django.urls import reverse
from uuid import uuid4

from .models import Coupon, redeem_done

COOKIE_NAME = 'coupon'


def set_coupon_cookie(coupon, response, token=None):
    """Update response with a group ordr token cookie."""
    ten_years = timedelta(days=(365 * 10))
    token = token or uuid4()
    response.set_signed_cookie(
        COOKIE_NAME, token, max_age=int(ten_years.total_seconds()))


def get_anonymous_coupon_token(request):
    return request.get_signed_cookie(COOKIE_NAME, default=None)


def get_anonymous_coupon(request):
    token = get_anonymous_coupon_token(request)
    return Coupon.unused.filter(code=token).first()


# def leave_giveaway_session(code, user):
#     user.coupon_set.get(code=code).leave()


# def redeem_coupon(coupon, user):
#     coupon.redeemed_at = datetime.now()
#     coupon.user = user
#     coupon.save(update_fields=['redeemed_at', 'user'])
#     send webhook
