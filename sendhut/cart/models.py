from decimal import Decimal
from collections import namedtuple

from django.db import models
from django.conf import settings
from django.dispatch import Signal
from jsonfield import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.encoding import smart_str

from sendhut.db import BaseModel
from sendhut.lunch.models import Item
from sendhut.utils import sane_repr


# signal
cart_updated = Signal(providing_args=['group_order', 'cart'])


CENTS = Decimal('0.01')

SimpleCart = namedtuple('SimpleCart', ('quantity', 'total', 'token'))


class CartStatus:
    """Enum of possible cart statuses."""

    OPEN = 'open'
    CANCELED = 'canceled'

    CHOICES = [
        (OPEN,  'Open - currently active'),
        (CANCELED, 'Canceled - canceled by user')

    ]


class Partition:

    def __init__(self, store, items):
        self.store = store
        self.items = items

    def get_delivery_cost(self):
        pass

    def get_total(self):
        return sum(line.get_total() for line in self.items)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return sum(line.quantity for line in self.items)


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


class Cart(BaseModel):
    """A shopping cart."""
    from uuid import uuid4

    class Meta:
        db_table = "cart"

    status = models.CharField(
        max_length=32, choices=CartStatus.CHOICES, default=CartStatus.OPEN)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='carts',
        on_delete=models.CASCADE)
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
                item=item, data=data or {}, defaults={'quantity': 1})

        return line

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

    def get_total(self):
        """Return the total cost of the cart prior to delivery."""
        return sum(line.get_total() for line in self.lines.all())

    def remove_line(self, line_id):
        self.lines.get(id=line_id).hard_delete()

    def clear(self):
        """Remove the cart."""
        self.hard_delete()

    def count(self):
        """Return the total quantity in cart."""
        lines = self.lines.all()
        return lines.aggregate(total_quantity=models.Sum('quantity'))

    def partitions(self):
        """Return the cart split into delivery/store groups.
        Generates tuples consisting of a partition, its delivery cost and its
        total cost.
        """
        from itertools import groupby
        for store, lines in groupby(self.lines.all(), key=lambda line: line.item.store):
            yield Partition(store, list(lines))

    def __len__(self):
        return self.lines.count()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the items from the database
        """
        return self.lines.all().iterator()

    __repr__ = sane_repr('token', 'user')


class CartLine(BaseModel):
    """A CartLine object represents a single line in a shopping cart
    Multiple lines in the same cart can refer to the same product if
    their `data` field is different.
    """
    cart = models.ForeignKey(
        Cart, related_name='lines', on_delete=models.CASCADE)
    item = models.ForeignKey(
        Item, related_name='+', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(999)])
    data = JSONField(blank=True, default={})

    class Meta:
        db_table = "cart_line"
        unique_together = ('cart', 'item', 'data')

    def __str__(self):
        return smart_str(self.item)

    def __eq__(self, other):
        if not isinstance(other, CartLine):
            return NotImplemented

        return (
            self.item == other.item and
            self.quantity == other.quantity and
            self.data == other.data)

    def __ne__(self, other):
        return not self == other  # pragma: no cover

    def __repr__(self):
        return 'CartLine(item=%r, quantity=%r, data=%r)' % (
            self.item, self.quantity, self.data)

    def __getstate__(self):
        return self.item, self.quantity, self.data

    def __setstate__(self, data):
        self.item, self.quantity, self.data = data

    def get_total(self):
        """Return the total price of this line."""
        total = self.get_price_per_item() * self.quantity
        # return total.amount.quantize(CENTS)
        return total

    def get_price_per_item(self):
        """Return the unit price of the line."""
        return self.item.get_price_per_item() + self._get_options_total()

    def _get_extras(self):
        extras = self.data.get('extras', [])
        _extras = []
        if extras:
            extras = list(map(int, extras))
            for option in Option.objects.filter(id__in=extras):
                _extras.append({
                    'id': option.id,
                    'uuid': str(option.uuid),
                    'name': option.name,
                    'price': option.price.amount if option.price else 0,
                    'parent': option.group.name
                })

        return _extras

    def _get_options_total(self):
        options = self._get_extras()
        return sum([x['price'] for x in options])
