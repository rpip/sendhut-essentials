class CouponStatus:
    """Enum of possible coupon states"""
    UNUSED = 'unused'
    REDEEMED = 'redeemed'

    CHOICES = [
        (UNUSED, "unused"),
        (REDEEMED, "redeemed")
    ]


class RedemptionDeniedException(Exception):
    pass


class InvalidGiveAwayException(Exception):
    pass
