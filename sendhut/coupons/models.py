from datetime import datetime

from django.conf import settings
from django.contrib.gis.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField
from django.dispatch import Signal
from safedelete.managers import SafeDeleteManager

from sendhut.db import BaseModel
from sendhut.utils import generate_token, sane_repr
from sendhut.accounts.models import Address
from . import CouponStatus


redeem_done = Signal(providing_args=["coupon"])


class CouponManager(SafeDeleteManager):
    # safedelete_visibility = DELETED_VISIBLE_BY_PK

    def create_coupon(self, value, users=[], campaign=None):
        coupon = self.create(
            value=value,
            code=Coupon.generate_code(),
            campaign=campaign
        )
        return coupon

    def create_coupons(self, quantity, value,
                       valid_until=None, campaign=None):
        coupons = []
        for i in range(quantity):
            coupon = self.create_coupon(value, valid_until, campaign)
            coupons.append(coupon)

        return coupons

    def used(self):
        return self.exclude(redeemed_at__isnull=True)

    def unused(self):
        return self.filter(redeemed_at__isnull=True)

    def expired(self):
        return self.filter(campaign__valid_until__lt=timezone.now())

    def spent(self):
        return self.filter(is_spent=True)


class Coupon(BaseModel):
    """
    The actual Coupon.

    Coupon is locked to user phone/email
    """
    ID_PREFIX = 'cpn'

    code = models.CharField(
        "Code", max_length=30, unique=True, blank=True,
        help_text="Leaving this field empty will generate a random code.")
    # allow different discounts for users in a campaign
    value = MoneyField(max_digits=10, decimal_places=2, default_currency=settings.DEFAULT_CURRENCY)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="User", null=True, blank=True)
    status = models.CharField(
        "Status", max_length=20,
        choices=CouponStatus.CHOICES, default=CouponStatus.UNUSED)
    campaign = models.ForeignKey(
        'Campaign', verbose_name="Campaign",
        blank=True, null=True, related_name='coupons')
    redeemed_at = models.DateTimeField("Redeemed at", blank=True, null=True)

    objects = CouponManager()

    class Meta:
        db_table = 'coupon'
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Coupon.generate_code()
        super(Coupon, self).save(*args, **kwargs)

    @classmethod
    def generate_code(cls, length=6):
        return generate_token(length)

    def user_can_redeem(self, user):
        # recipient = self.metadata['recipient']
        # return recipient.phone == user.phone
        return True

    @property
    def monetary_value(self):
        """
        Returns coupon specific value if set.
        Otherwise returns campaign discount valaue
        """
        return self.value or self.campaign.value

    __repr__ = sane_repr('code', 'user',)

    def __str__(self):
        return self.code


class Campaign(BaseModel):
    "A campaign is like a promo. Coupons belong to campaigns"
    ID_PREFIX = 'cpn'

    name = models.CharField("Name", max_length=255, unique=True)
    description = models.TextField("Description", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="User")
    user_limit = models.PositiveIntegerField("User limit", default=1)
    value = MoneyField(max_digits=10, decimal_places=2, default_currency=settings.DEFAULT_CURRENCY)
    valid_until = models.DateTimeField(
        "Valid until", blank=True, null=True,
        help_text="Leave empty for coupons that never expire")

    @property
    def is_expired(self):
        return self.valid_until is not None \
            and self.valid_until < timezone.now()

    class Meta:
        db_table = 'campaign'
        ordering = ['name']
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"

    __repr__ = sane_repr('name',)

    def __str__(self):
        return self.name


class CampaignDropoff(BaseModel):
    "Addresses linked to campaigns for delivery"

    ID_PREFIX = 'cpndrp'

    campaign = models.ForeignKey(Campaign, related_name='addresses')
    address = models.ForeignKey(Address, verbose_name="Address")
    # TODO(yao): lock coupon to certain restaurants

    class Meta:
        db_table = 'campaign_dropoff'
        unique_together = (('campaign', 'address'),)

    __repr__ = sane_repr('campaign', 'address')

    def __str__(self):
        return self.id
