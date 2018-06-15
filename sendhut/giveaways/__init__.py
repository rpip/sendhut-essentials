class CouponStatus:
    """Enum of possible coupon states"""
    UNUSED = 'unused'
    USED = 'used'
    REDEEMED = 'redeemed'

    CHOICES = [
        (UNUSED, "unused"),
        (USED, "used"),
        (REDEEMED, "redeemed")
    ]


class RedemptionDeniedException(Exception):
    pass


class InvalidGiveAwayException(Exception):
    pass
