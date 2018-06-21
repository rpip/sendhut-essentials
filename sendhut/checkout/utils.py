from django.conf import settings
from djmoney.money import Money

from sendhut.grouporder.utils import get_store_group_order_cookie_name
from sendhut.accounts.models import Address
from sendhut.utils import windows_from_time_string
from .models import Order, OrderLine


class Checkout:
    """Represents a checkout session."""

    def __init__(self, cart, user):
        self.cart = cart
        self.user = user
        self.delivery_address = None
        self.delivery_time = None
        self.order = None

    def create_order(self, **kwargs):
        """Create an order from the checkout session.

        If any of the addresses is new and the user is logged in the address
        will also get saved to that user's address book.
        """
        payment_reference = kwargs.pop('payment_reference', None)
        cash = kwargs.pop('cash', None)
        # address = kwargs.get('address')
        # delivery_point = kwargs.get('delivery_point')
        # if address:
        #     kwargs['address'] = Address.objects.create(user=self.user, address=address)
        # else:
        #     kwargs['address'] = Address.objects.get(id=delivery_point)

        if self.cart.is_in_group_order():
            order = self._create_group_order(**kwargs)
        else:
            order = self._create_single_order(**kwargs)

        if not(cash):
            order.set_payment_online(payment_reference)

        if self.user.coupon:
            order.coupon = self.user.coupon
            order.save(update_fields=['coupon'])
            self.user.coupon.leave()

        return order

    def _create_group_order(self, time, date, address, notes=None):
        group_order = self.cart.get_group_order()
        group_order.lock()
        self.order = Order.objects.create(
            user=self.user,
            delivery_time=time,
            delivery_date=date,
            address=address,
            notes=notes,
            total_gross=self.get_total(),
            group_order=group_order,
            delivery_fee=self.calculate_delivery_cost()
        )
        return self.order

    def _create_single_order(self, time, date, address, notes=None):
        self.order = Order.objects.create(
            user=self.user,
            delivery_time=time,
            delivery_date=date,
            address=address,
            delivery_fee=self.calculate_delivery_cost(),
            total_gross=self.get_total(),
            notes=notes
        )

        for line in self.cart.lines.all():
            self.add_item_to_order(self.order, line.item, line.quantity, line.data)

        # delete cart after checkout
        self.cart.delete()
        return self.order

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


def do_checkout_cleanup(response, order):
    if order.group_order:
        cookie_name = get_store_group_order_cookie_name(order.group_order.store)
        response.delete_cookie(cookie_name)
