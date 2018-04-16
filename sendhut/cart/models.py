from collections import namedtuple

from django.db import models
from django.conf import settings
from jsonfield import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from sendhut.db import BaseModel
from sendhut.utils import sane_repr
from sendhut.lunch.models import Item

from . import CartStatus
from .core import partition, ItemSet, ItemLine, ItemList


SimpleCart = namedtuple('SimpleCart', ('quantity', 'total', 'token'))


class CartQueryset(models.QuerySet):
    """A specialized queryset for dealing with carts."""

    def anonymous(self):
        """Return unassigned carts."""
        return self.filter(user=None)

    def open(self):
        """Return `OPEN` carts."""
        return self.filter(status=CartStatus.OPEN)

    def canceled(self):
        """Return `CANCELED` carts."""
        return self.filter(status=CartStatus.CANCELED)


class Cart(BaseModel, ItemSet):
    """A shopping cart."""
    from uuid import uuid4

    class Meta:
        db_table = "cart"

    status = models.CharField(
        max_length=32, choices=CartStatus.CHOICES, default=CartStatus.OPEN)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='carts')
    token = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    objects = CartQueryset.as_manager()
    # TODO(yao): cart for anonymous user
    # TODO(yao): cart views CRUD
    # TODO(yao): transfer anonymous to user
    # TODO(yao): transfer anonymous to user
    # TODO(yao): group cart

    def add(self, item, quantity=1, data=None, replace=False):
        """Add an item to cart.
        Items are considered identical if both item and data are equal.

        The `data` parameter may be used to differentiate between items with
        different customization options.

        This allows you to customize two copies of the same item
        (eg. choose different toppings) and track their quantities
        independently.
        """
        if replace:
            # update cart_line qty and data
            line = self.lines.get(id=data.get('line_id'))
            line.quantity = quantity
            line.data = data or {}
            line.save(update_fields=['quantity', 'data'])
        else:
            # TODO(yao): handle adding dif qty for line if same data
            line, created = self.lines.get_or_create(
                item=item, data=data or {}, defaults={'quantity': quantity})

        return line

    def load_from_cart(self, other_cart):
        return other_cart.lines.update(cart=self)

    def create_line(self, item, quantity, data):
        """Create a cart line for given item, quantity and optional data.
        The `data` parameter may be used to differentiate between items with
        different customization options.
        """
        return self.lines.create(
            item=item, quantity=quantity, data=data or {})

    def get_line(self, item, data=None):
        """Return a line matching the given item and data if any."""
        all_lines = self.lines.all()
        if data is None:
            data = {}
        line = [
            line for line in all_lines
            if line.item_id == item.id and line.data == data]
        if line:
            return line[0]
        return None

    def change_status(self, status):
        """Change cart status."""
        if status not in dict(CartStatus.CHOICES):
            raise ValueError('Not expected status')
        if status != self.status:
            self.status = status
            self.save()

    def change_user(self, user):
        """Assign cart to a user."""
        # TODO(yao): what if user has carts across devices?
        # TODO(yao): delete old carts. no activity after 1 hr
        self.user = user
        self.save(update_fields=['user'])

    def remove_line(self, line_id):
        self.lines.get(id=line_id).hard_delete()

    def clear(self):
        """Remove the cart."""
        self.hard_delete()

    def partitions(self):
        "Return the cart split into delivery/store groups"
        return partition(self, lambda line: line.item.store, ItemList)

    def is_in_group_order(self):
        return getattr(self, 'group_member', None)

    def get_group_order(self):
        return self.group_member.group_order

    def lock(self):
        self.update(status=CartStatus.LOCKED)

    def is_empty(self):
        return not(len(self))

    def __len__(self):
        return self.lines.count()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the items from the database
        """
        return self.lines.all().iterator()

    __repr__ = sane_repr('token', 'user')


class CartLine(BaseModel, ItemLine):
    """A CartLine object represents a single line in a shopping cart
    Multiple lines in the same cart can refer to the same product if
    their `data` field is different.
    """
    cart = models.ForeignKey(
        Cart, related_name='lines', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='+', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(999)])
    data = JSONField(blank=True, default={})

    class Meta:
        db_table = "cart_line"
        unique_together = ('cart', 'item', 'data')

    def __repr__(self):
        return 'CartLine(item=%r, quantity=%r, data=%r)' % (
            self.item, self.quantity, self.data)
