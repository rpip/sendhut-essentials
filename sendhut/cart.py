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
        price_per_item = self.get_price_per_item(**kwargs)
        quantity = self.get_quantity(**kwargs)
        return quantity * price_per_item

    def get_price_per_item(self, **kwargs):
        """
        Tthe price of a single piece of the item
        """
        pass

    def get_quantity(self, **kwargs):
        """
        Returns the quantity of the item
        """
        pass


class CartLine(ItemLine):
    """
    A CartLine object represents a single line in a shopping cart
    """

    def __init__(self, product, quantity, data=None):
        pass

    def get_total(self):
        pass

    def get_price_per_item(self):
        pass


class Cart:
    """
    A Cart object represents a shopping cart
    """

    def __init__(self):
        pass

    def __iter__(self):
        """
        Returns an iterator that yields CartLine objects contained
        in the cart.
        """

    @property
    def modified(self):
        pass

    def add(product, quantity=1, data=None, replace=False):
        """
        If replace is False, increases quantity of the given product
        by quantity. If given product is not in the cart yet, a new line
        is created.

        If replace is True, quantity of the given product is set to quantity.
        If given product is not in the cart yet, a new line is created.

        If the resulting quantity of a product is zero, its line is removed
        from the cart.

        Products are considered identical if both product and data are equal.
        This allows you to customize two copies of the same product
        (eg. choose different toppings) and track their quantities
        independently.
        """
        pass

    def get_total(self):
        """
        Return a prices.Price object representing the total price of
        the cart.
        """
        pass

    def check_quantity(self, product, quantity, data):
        """
        Checks if given quantity is valid for the product and its data.
        """
        pass

    def create_line(self, product, quantity, data):
        """
        Creates a CartLine given a product, its quantity and data
        """
        pass

    def process(self):
        pass
