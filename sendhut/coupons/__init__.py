"""
version 1:
- can't use coupons on group order
-
"""


class CouponStatus:
    """Enum of possible coupon states"""
    UNUSED = 'unused'
    USED = 'used'
    EXPIRED = 'expired'

    CHOICES = [
        (UNUSED, "unused"),
        (USED, "used"),
        (EXPIRED, "expired")
    ]


class CouponTypes:
    MONETARY = 'monetary'
    PERCENTAGE = 'percentage'

    CHOICES = [
        (MONETARY, 'Money based coupon'),
        (PERCENTAGE, 'Percentage discount')
    ]


class RedemptionDeniedException(Exception):
    pass


class InvalidCouponException(Exception):
    pass
