from datetime import datetime, timedelta
from django.http import Http404
from django.core.urlresolvers import resolve
from django.urls import reverse
from uuid import uuid4

from .models import Coupon, redeem_done

COOKIE_NAME = 'coupon'


def set_coupon_cookie(coupon, req, resp):
    ten_years = timedelta(days=(365 * 10))
    resp.set_signed_cookie(
        COOKIE_NAME, coupon.code, max_age=int(ten_years.total_seconds()))

    return get_coupon_token(req)


def get_coupon_token(request):
    return request.get_signed_cookie(COOKIE_NAME, default=None)


def get_coupon_from_request(request):
    token = get_coupon_token(request)
    return Coupon.objects.unused().filter(code=token).first()


def leave_giveaway_session(response):
    return response.delete_cookie(COOKIE_NAME)


# def redeem_coupon(coupon, user):
#     coupon.redeemed_at = datetime.now()
#     coupon.user = user
#     coupon.save(update_fields=['redeemed_at', 'user'])
#     send webhook
