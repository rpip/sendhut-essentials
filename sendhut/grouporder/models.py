from django.db import models
from django.conf import settings
from django.urls import reverse

from djmoney.money import Money
from djmoney.models.fields import MoneyField

from sendhut.db import BaseModel
from sendhut.stores.models import Store
from sendhut.cart import CartStatus
from sendhut.cart.models import Cart
from sendhut.utils import generate_token, sane_repr
from . import MemberStatus


class GroupOrderMixin(models.Model):
    status = models.CharField(
        max_length=32, choices=CartStatus.CHOICES, default=CartStatus.OPEN)

    def get_subtotal(self):
        raise NotImplementedError

    def get_total(self):
        raise NotImplementedError

    def __str__(self):
        return self.token

    class Meta:
        abstract = True


class GroupOrderMemberMixin(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    def get_cart_total(self):
        return self.cart.get_subtotal()

    def get_name(self):
        # return self.name or self.user.get_full_name()
        return self.user.get_full_name() if self.is_cart_owner() else self.name

    def leave(self):
        self.state = MemberStatus.OUT
        self.save(update_fields=['state'])

    def join(self):
        self.update(state=MemberStatus.IN)

    def is_active(self):
        return self.state == MemberStatus.IN

    class Meta:
        abstract = True


class GroupOrder(GroupOrderMixin, BaseModel):
    """
    Model for holding group orders.
    """
    # TODO(yao): enforce group order limit
    ID_PREFIX = 'gord'

    monetary_limit = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency=settings.DEFAULT_CURRENCY,
        null=True,
        blank=True
    )
    # TODO(yao): rename user -> created_by
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='group_orders')
    store = models.ForeignKey(Store)
    token = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        # TODO(yao): generate Heroku-style names for the group order
        if not self.created:
            self.token = generate_token(6)
        super().save(*args, **kwargs)
        return self

    def lock(self):
        # TODO(yao): run check to lock all expired groups orders
        self.update(status=CartStatus.LOCKED)
        for member in self.members.all():
            member.cart.lock()

    def unlock(self):
        self.update(status=CartStatus.OPEN)

    def cancel(self):
        for x in self.members.all():
            x.cart.hard_delete()
            x.hard_delete()

        self.delete()

    def is_open(self):
        return self.status == CartStatus.OPEN

    def find_member(self, user):
        return Member.objects.filter(user=user).first()

    def get_subtotal(self):
        return sum(x.get_cart_total() for x in self.members.all())

    def get_total(self):
        # TODO(yao): get total + delivery
        return self.get_subtotal() + self.get_bowl_charge_total() + \
            Money(settings.BASE_DELIVERY_FEE, 'NGN')

    def get_bowl_charge_total(self):
        return sum(x.cart.bowl_charge_total for x in self.members.all())

    def get_absolute_url(self):
        return reverse('cart_join', args=(self.token, ))

    class Meta:
        db_table = "group_order"

    __repr__ = sane_repr('token')


class Member(BaseModel, GroupOrderMemberMixin):

    ID_PREFIX = 'mbr'

    class Meta:
        db_table = "member"
        unique_together = ('group_order', 'user')

    name = models.CharField(max_length=40)
    group_order = models.ForeignKey(
        GroupOrder, related_name='members',
        on_delete=models.CASCADE)
    cart = models.OneToOneField(
        Cart, related_name='group_member', on_delete=models.CASCADE)
    state = models.CharField(
        max_length=32, choices=MemberStatus.CHOICES, default=MemberStatus.OUT)

    def is_cart_owner(self):
        return self.user == self.group_order.user

    __repr__ = sane_repr('id', 'name')
