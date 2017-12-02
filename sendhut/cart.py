from itertools import groupby
from decimal import Decimal

from django.conf import settings

from sendhut.lunch.models import Item, SideItem


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
        self.uuid = str(item.uuid)
        self.quantity = quantity
        self.data = data or {}

    def get_price_per_item(self, **kwargs):
        return self.get_base_price() + self._get_options_total()

    def get_base_price(self):
        return Decimal(self.data['price'])

    def _get_extras(self):
        extras = self.data.pop('extras', [])
        if extras:
            extras = list(map(int, extras))
            _extras = []
            for x in SideItem.objects.filter(id__in=extras):
                _extras.append({
                    'uuid': x.uuid,
                    'name': x.name,
                    'price': x.price.amount,
                    'parent': x.menu.name
                })

            _extras = [(c, list(cgen)) for c, cgen in
                       groupby(_extras, lambda x: x['parent'])]
            return dict(_extras)
        return {}

    def _get_options_total(self):
        options = self._get_extras()
        return sum([x['price'] for x in sum(options.values(), [])])

    def serialize(self):
        _data = {
            'uuid': self.uuid,
            'quantity': self.quantity,
            'unit_price': self.get_price_per_item(),
            'base_price': self.get_base_price(),
            'total': self.get_total(),
            'options': self._get_extras(),
        }
        _data.update(self.data)
        return _data


class Cart:
    """
    A Cart object represents a shopping cart
    """

    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.modified = False
        self.session = request.session
        self._state = []
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty in the session
            cart = self.session[settings.CART_SESSION_ID] = []

        class obj(object):
            def __init__(self, d):
                self.__dict__ = d

        for l in [obj(x) for x in cart]:
            self.add(l, l.quantity, l.data)

    def add(self, item, quantity=1, data=None, replace=False):
        """
        If replace is False, increases quantity of the given item
        by quantity. If given item is not in the cart yet, a new line
        is created.

        If replace is True, quantity of the given item is set to quantity.
        If given item is not in the cart yet, a new line is created.

        If the resulting quantity of a item is zero, its line is removed
        from the cart.

        Items are considered identical if both item and data are equal.
        This allows you to customize two copies of the same item
        (eg. choose different toppings) and track their quantities
        independently.
        """
        # TODO(yao): Implement item replacement
        line = self.get_line(item, quantity, data)
        if not line:
            line = self.create_line(item, int(quantity), data)
            self._state.append(line)
            self.save()

    def get_line(self, item, quantity, data):
        return next((cart_line for cart_line in self._state if
                    cart_line.uuid == item.uuid
                    and cart_line.quantity == quantity
                    and cart_line.data == data), None)

    def create_line(self, item, quantity, data):
        """
        Creates a CartLine given a item, its quantity and data
        """
        return CartLine(item, quantity, data)

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.serialize_lite()
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

    def remove(self, item, quantity, data):
        """Remove a item from the cart"""
        cart_line = self.get_line(item, quantity, data)
        self._state.remove(cart_line)
        self.save()

    def get_subtotal(self):
        """
        Return the total price of the cart.
        """
        return sum([cart_line.get_total() for cart_line in self._state])

    def process(self):
        # TODO(yao): implement multiple step processor a la satchless
        pass

    def __iter__(self):
        """
        Iterate over the items in the cart and get the items from the database
        """
        # TODO(yao): group extras by option_group
        # TODO(yao): rename extras to options
        return iter(self._state)

    def __getitem__(self, key):
        return self._state[key]

    def __len__(self):
        return len(self._state)

    def __repr__(self):
        return 'Cart(%r)' % (list(self),)
