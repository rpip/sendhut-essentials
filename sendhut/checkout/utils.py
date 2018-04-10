from django.conf import settings
from djmoney.money import Money

from .models import Order, OrderLine


class Checkout:
    """Represents a checkout session."""

    def __init__(self, cart, user):
        self.cart = cart
        self.user = user
        self.delivery_address = None
        self.delivery_time = None
        self.order = None

    def create_order(self, time, address=None, notes=None):
        """Create an order from the checkout session.

        If any of the addresses is new and the user is logged in the address
        will also get saved to that user's address book.
        """
        order = Order.objects.create(
            user=self.user, time=time, address=address,
            notes=notes, delivery_fee=self.calculate_delivery_cost(),
            total_gross=self.get_total()
        )

        for line in self.cart.lines.all():
            self.add_item_to_order(order, line.item, line.quantity, line.data)

        self.order = order

        # self.cart.delete()
        return order

    def add_item_to_order(self, order, item, quantity, metadata):
        return OrderLine.objects.create(
            order=order,
            item=item,
            unit_price=item.price,
            quantity=quantity,
            special_instructions=metadata.pop('note', None),
            metadata=metadata
        )

    def get_subtotal(self):
        """Calculate order total without shipping and discount."""
        return self.cart.get_total()

    def get_total(self):
        """Calculate order total with shipping and discount amount."""
        return self.get_subtotal() + self.calculate_delivery_cost()

    def calculate_delivery_cost(self):
        return Money(settings.BASE_DELIVERY_FEE, settings.DEFAULT_CURRENCY)
