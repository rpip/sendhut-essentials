"""
- add to cart
 - if has item from another cart, warn that and ask if to start new cart
- see cart and modify
- checkout: select delivery address and (time [confirm if must select same delivery time for
all orders, deliver orders to the addresses at the same time]).
"""
from django.urls import reverse
from datetime import datetime
from django.conf import settings
from django.contrib.gis.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField
from django.dispatch import Signal
from safedelete.managers import SafeDeleteManager

from sendhut.db import BaseModel
from sendhut.grouporder.models import GroupOrderMixin, GroupOrderMemberMixin
from sendhut.utils import generate_token, sane_repr
from sendhut.stores.models import Store
from sendhut.accounts.models import Address


redeem_done = Signal(providing_args=["coupon"])


class CouponManager(SafeDeleteManager):
    # safedelete_visibility = DELETED_VISIBLE_BY_PK

    def create_coupon(self, giveaway):
        coupon = self.create(code=Coupon.generate_code(), giveaway=giveaway)
        return coupon

    def create_coupons(self, quantity, giveaway):
        coupons = []
        for i in range(quantity):
            coupon = self.create_coupon(giveaway)
            coupons.append(coupon)

        return coupons

    def redeemed(self):
        return self.filter(redeemed_at__isnull=False)

    def unused(self):
        return self.filter(redeemed_at__isnull=True)


class Coupon(GroupOrderMemberMixin, BaseModel):
    # TODOY(yao): don't cascade coupons to giveaway.
    ID_PREFIX = 'givc'

    code = models.CharField("Code", max_length=30, unique=True, blank=True)
    giveaway = models.ForeignKey('GiveAway', verbose_name="GiveAway", related_name='coupons')
    redeemed_at = models.DateTimeField(null=True, blank=True)

    objects = CouponManager()

    def get_absolute_url(self):
        return reverse('join', args=(self.code, ))

    @property
    def stores(self):
        return [x.address for x in self.giveaway.addresses.all()]

    @property
    def addresses(self):
        return [x.address for x in self.giveaway.addresses.all()]

    @property
    def cart(self):
        return self.user.cart

    @property
    def discount_value(self):
        return self.giveaway.discount_value

    @property
    def get_store(self):
        # lock coupon to store where first item is add
        # when cart is empty remove lock.
        # repeat
        if self.cart.lines.first():
            return self.cart.lines.first().item.store

    def mark_redeemed(self):
        self.redeemed_at = datetime.now()
        self.save(update_fields=['redeemed_at'])

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Coupon.generate_code()
        super().save(*args, **kwargs)

    @classmethod
    def generate_code(cls, length=6):
        return generate_token(length)

    class Meta:
        db_table = "coupon"
        unique_together = ('giveaway', 'user', 'code')

    __repr__ = sane_repr('code', 'user',)

    def __str__(self):
        return self.code


class GiveAwayManager(SafeDeleteManager):
    # safedelete_visibility = DELETED_VISIBLE_BY_PK

    def create_giveaway(self, discount_value, valid_until=None):
        pass

    def expired(self):
        return self.filter(valid_until__lt=timezone.now())


class GiveAway(GroupOrderMixin, BaseModel):
    """A giveaway is like a promo.

    alpha: no discount check. just join and place order
    """
    ID_PREFIX = 'giv'

    name = models.CharField("Name", max_length=255, unique=True)
    description = models.TextField("Description", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="User", related_name='giveaways')
    valid_until = models.DateTimeField(
        "Valid until", blank=True, null=True,
        help_text="Leave empty for coupons that never expire")
    discount_value = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency=settings.DEFAULT_CURRENCY,
        null=True,
        blank=True
    )

    def get_stores(self):
        return [x.store for x in self.stores.all()]

    @property
    def is_open(self):
        return not(self.is_expired()) or (self.status == CartStatus.OPEN)

    def cancel(self):
        self.delete()

    @property
    def is_expired(self):
        return self.valid_until is not None \
            and self.valid_until < timezone.now()

    def lock(self):
        # TODO(yao): run check to lock all expired groups orders
        self.update(status=CartStatus.LOCKED)

    def get_subtotal(self):
        return self.discount_value * self.coupons.redeemed().count()

    def get_total(self):
        return self.get_subtotal()

    class Meta:
        db_table = 'giveaway'
        verbose_name = "GiveAway"
        verbose_name_plural = "GiveAways"

    __repr__ = sane_repr('name',)

    def __str__(self):
        return self.name


class GiveAwayDropoff(BaseModel):
    "Addresses linked to giveaways for delivery"

    ID_PREFIX = 'givdrp'

    giveaway = models.ForeignKey(GiveAway, related_name='addresses')
    address = models.ForeignKey(Address, related_name="giveaways")

    class Meta:
        db_table = 'giveaway_dropoff'
        unique_together = (('giveaway', 'address'),)

    __repr__ = sane_repr('giveaway', 'address')


class GiveAwayStore(BaseModel):
    "Stores linked to giveaways for delivery"

    ID_PREFIX = 'gifstr'

    giveaway = models.ForeignKey(GiveAway, related_name='stores')
    store = models.ForeignKey(Store, related_name='giveaways')

    class Meta:
        db_table = 'giveaway_store'
        unique_together = (('giveaway', 'store'),)

    __repr__ = sane_repr('giveaway', 'store')
