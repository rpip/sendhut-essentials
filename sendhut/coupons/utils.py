from datetime import datetime

from .models import Coupon, redeem_done
from . import RedemptionDeniedException


def redeem_coupon(code, user):
    coupon = Coupon.objects.unused().get(code=code)
    if coupon.user_can_redeem(user):
        coupon.redeemed_at = datetime.now()
        coupon.user = user
        coupon.save(update_fields=['redeemed_at', 'user'])
        redeem_done.send(sender=coupon.__class__, coupon=coupon)
        return coupon

    raise RedemptionDeniedException(coupon)
