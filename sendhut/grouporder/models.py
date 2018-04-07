from django.conf import settings
from django.urls import reverse
from django.db import models

from djmoney.models.fields import MoneyField

from sendhut.db import BaseModel
from sendhut.utils import build_absolute_uri
from sendhut.lunch.models import Store
from sendhut.cart.models import Cart, CartStatus
from sendhut.utils import generate_token


class GroupOrder(BaseModel):
    """
    Model for holding group orders.
    """
    # TODO(yao): enforce group order limit
    class Meta:
        db_table = "group_order"

    token = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='group_orders')
    store = models.ForeignKey(Store)
    monetary_limit = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency=settings.DEFAULT_CURRENCY,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=32, choices=CartStatus.CHOICES, default=CartStatus.OPEN)

    @staticmethod
    def get_user_open_carts(user):
        return GroupOrder.objects.filter(
            members__user=user, status=CartStatus.OPEN)

    def save(self, *args, **kwargs):
        # TODO(yao): generate Heroku-style names for the group order
        if not self.created:
            self.token = generate_token(6)
        super().save(*args, **kwargs)
        return self

    def lock(self):
        self.update(status=self.LOCKED)

    def unlock(self):
        self.update(status=self.OPEN)

    def is_open(self):
        return self.status == self.OPEN

    def cancel(self):
        for x in self.members.all():
            x.cart.hard_delete()
            x.hard_delete()

        self.hard_delete()

    def get_total(self):
        return sum(x.get_total() for x in self.members.all())

    def get_absolute_url(self):
        return reverse('cart_join', args=(self.token, ))

    def get_share_url(self):
        url = reverse('join-group-order', args=(self.token,))
        return build_absolute_uri(url)

    def __str__(self):
        return self.token


class MemberStatus:
    """Enum of possible member modes/states"""
    IN = 'in'
    OUT = 'out'

    CHOICES = [
        (IN,  'IN - currently active'),
        (OUT, 'OUT - exited by user')
    ]


class Member(BaseModel):

    class Meta:
        db_table = "member"
        unique_together = ('group_order', 'user')

    group_order = models.ForeignKey(GroupOrder, related_name='members')
    name = models.CharField(max_length=40)
    cart = models.OneToOneField(
        Cart, related_name='group_member', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # if group order isn't locked/cancelled, user can go in/out anytime
    state = models.CharField(
        max_length=32, choices=MemberStatus.CHOICES, default=MemberStatus.IN)

    def get_cart_total(self):
        return self.cart.get_total()

    def is_cart_owner(self):
        return self.user == self.group_order.user

    def get_name(self):
        return self.cart.user.get_full_name() if self.cart.user else self.name

    def leave(self):
        self.mode = MemberStatus.OUT

    def rejoin(self):
        self.mode = MemberStatus.IN

    def is_in_session(self):
        self.state == MemberStatus.IN
