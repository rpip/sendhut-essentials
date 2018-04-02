from itertools import groupby
from decimal import Decimal

from django.conf import settings
from django.dispatch import Signal

from sendhut.lunch.models import Option, GroupCartMember
from sendhut.lunch.group_order import GroupOrder
from sendhut import utils
#from sendhut.api.serializers import (
#    GroupCartSerializer, GroupCartMemberSerializer
#)


# signal
cart_updated = Signal(providing_args=['group_order', 'cart'])


class ItemLine:
    """
    An ItemLine instance represents a certain quantity of a particular
    priceable.
    """
    def get_total(self, **kwargs):
        """
        The total price of the line.
        Keyword arguments are passed to both get_quantity() and
        get_price_per_item().
        """
        return self.get_price_per_item(**kwargs) * self.get_quantity(**kwargs)

    def get_price_per_item(self, **kwargs):
        """
        The price of a single piece of the item
        """
        raise NotImplementedError()

    def get_quantity(self, **kwargs):
        """
        Returns the quantity of the item
        """
        return self.quantity


class CartLine(ItemLine):
    """
    A CartLine object represents a single line in a shopping cart
    """
    def __init__(self, item, quantity, data=None):
        from uuid import uuid4
        data = data or {}
        # add line id for fresh line
        if not data.get('line_id'):
            data['line_id'] = uuid4().hex
        self.id = item.id
        self.quantity = quantity
        self.data = data

    def get_price_per_item(self, **kwargs):
        return self.get_base_price() + self._get_options_total()

    def get_base_price(self):
        price = self.data['price'] if self.data['price'] else 0
        return Decimal(price)

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

    def serialize(self):
        # TODO(yao): rename extras to options
        extras = self.data.get('extras', [])
        _data = {
            'quantity': self.quantity,
            'unit_price': self.get_price_per_item(),
            'base_price': self.get_base_price(),
            'total': self.get_total(),
            'extras_meta': self._get_extras(),
            'extras': list(map(int, extras))
        }
        import copy
        _line = copy.deepcopy(self.data)
        _line.update(_data)
        return {'id': self.id, 'quantity': self.quantity, 'data': _line}


class Cart:
    """
    A Cart object represents a shopping cart
    """
    class Line(object):
        def __init__(self, d):
            self.__dict__ = d

    def __init__(self, request, items=None):
        """
        Initialize the cart.

        Attempts to load cart from session or adds items from the
        items parameter passed. Items must list of serialized cart lines.
        """
        self.modified = False
        self.session = request.session
        self._state = []
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty in the session
            cart = self.session[settings.CART_SESSION_ID] = []

        self._preload_cart(cart)

        if items:
            for l in [self.Line(x) for x in items]:
                self.add(l, l.quantity, l.data)

    def _preload_cart(self, cart):
        # cart._state is a list of dictionaries. convert to objects
        for l in [self.Line(x) for x in cart]:
            self.add(l, l.quantity, l.data)

    def add(self, item, quantity=1, data=None, replace=False):
        """
        Items are considered identical if both item and data are equal.
        This allows you to customize two copies of the same item
        (eg. choose different toppings) and track their quantities
        independently.
        """
        line = self.match_line(item, quantity, data)
        if replace:
            self.remove(data.get('line_id'))

        if line:
            self.remove(line.data['line_id'])

        line = self.create_line(item, int(quantity), data)
        self._state.append(line)
        self.save()

    def match_line(self, item, quantity, data):
        "Matches: item uuid, extra (sides/options)"
        extras = list(map(int, data.get('extras', [])))
        return next((line for line in self._state if
                     line.id == item.id and
                     line.quantity == quantity and
                     line.data.get('extras') == extras), None)

    def get_line(self, line_id):
        """
        Returns False if item match is not found.
        """
        return next((line for line in self._state if
                     line.data['line_id'] == line_id), None)

    def create_line(self, item, quantity, data):
        """
        Creates a CartLine given a item, its quantity and data
        """
        return CartLine(item, quantity, data)

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.serialize()
        self.session.modified = True
        self.modified = True

    def serialize(self):
        return [x.serialize() for x in self._state]

    def serialize_lite(self):
        return [x.__dict__ for x in self._state]

    def clear(self):
        self._state = []
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
        self.modified = True

    def remove(self, line_id):
        """Remove a item from the cart"""
        cart_line = self.get_line(line_id)
        self._state.remove(cart_line)
        self.save()

    def get_subtotal(self):
        """
        Return the total price of the cart.
        """
        return sum([cart_line.get_total() for cart_line in self._state])

    def __iter__(self):
        """
        Iterate over the items in the cart and get the items from the database
        """
        return iter(self._state)

    def __getitem__(self, key):
        return self._state[key]

    def __len__(self):
        return len(self._state)

    def __repr__(self):
        return 'Cart(%r)' % (list(self),)

    def build_cart(self):
        # TODO(yao): move delivery fee, sub_total to context processor
        sub_total = self.get_subtotal()
        delivery_fee = settings.LUNCH_DELIVERY_FEE
        cart_delivery_fee = delivery_fee * len(self)
        total = sub_total + cart_delivery_fee
        cart = self.serialize()
        store_grouped_cart = [
            (x, list(y)) for x, y in
            groupby(cart, lambda x: x['data']['store']['name'])]
        return {
            'cart': cart,
            'store_grouped_cart': store_grouped_cart,
            'sub_total': sub_total,
            'delivery_fee': delivery_fee,
            'cart_delivery_fee': cart_delivery_fee,
            'total': total
        }

    def load(self, data):
        """
        Loads cart from JSON data, built specifically for loading
        cart from group order member carts"""
        for line in data:
            self.add(line.pop('uuid'), line.pop('quantity'), data=line)


class GroupMemberCart(Cart):

    def __init__(self, request, cart_token):
        """
        Initialize the cart.

        Attempts to load cart from session or adds items from the
        items parameter passed. Items must list of serialized cart lines.
        """
        self.group_order = GroupOrder.get(request, cart_token)
        member_id = self.group_order['member']['id']
        self.member = GroupCartMember.objects.get(id=member_id)
        self._state = []
        self._preload_cart(self.member.cart)

    def save(self):
        self.member.cart = self.serialize()
        self.member.save()

    def build_cart(self):
        data = super().build_cart()
        data['group_order'] = self.group_order
        return data
