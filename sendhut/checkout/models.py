from django.urls import reverse
from django.conf import settings
from django.contrib.gis.db import models
from jsonfield import JSONField
from djmoney.models.fields import MoneyField

from sendhut.db import BaseModel
from sendhut.accounts.models import Address
from sendhut.stores.models import Item
from sendhut.cart.core import ItemLine, ItemSet, ItemList, partition
from sendhut.grouporder.models import GroupOrder
from sendhut.giveaways.models import Coupon
from sendhut.utils import generate_token, sane_repr, asap_delivery_estimate
from . import PaymentStatus, PaymentSource, OrderStatus


class OrderQueryset(models.QuerySet):

    def confirmed(self):
        return self.exclude(status=OrderStatus.PENDING)

    def drafts(self):
        return self.filter(status=OrderStatus.PENDING)

    # def to_ship(self):
    #     """Fully paid but unfulfilled (or partially fulfilled) orders."""
    #     statuses = {OrderStatus.UNFULFILLED, OrderStatus.PARTIALLY_FULFILLED}
    #     return self.filter(status__in=statuses).annotate(
    #         amount_paid=Sum('payments__captured_amount')).filter(
    #         total_gross__lte=F('amount_paid'))


class Order(BaseModel, ItemSet):

    ID_PREFIX = 'ord'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders')
    reference = models.CharField(max_length=8, unique=True)
    # TODO(yao): Add types of orders:
    #   Orders that have already been placed:
    #   Orders that are placed and paid for
    #   Manual payment and order:
    delivery_date = models.DateTimeField()
    delivery_time = models.DateTimeField(default=asap_delivery_estimate)
    # TODO(yao): save address as Address model
    address = models.ForeignKey(Address)
    delivery_fee = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency=settings.DEFAULT_CURRENCY
    )
    notes = models.CharField(max_length=300, null=True, blank=True)
    total_gross = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency=settings.DEFAULT_CURRENCY
    )
    status = models.CharField(
        max_length=32,
        choices=OrderStatus.CHOICES,
        default=OrderStatus.PENDING
    )
    payment_reference = models.CharField(max_length=32, blank=True, null=True)
    payment_status = models.CharField(
        max_length=32,
        choices=PaymentStatus.CHOICES,
        default=PaymentStatus.PENDING
    )
    payment_source = models.CharField(
        max_length=32,
        choices=PaymentSource.CHOICES,
        default=PaymentSource.CASH
    )
    group_order = models.OneToOneField(
        GroupOrder, related_name='order', null=True, blank=True)
    coupon = models.OneToOneField(
        Coupon, related_name='order', null=True, blank=True)

    def update_payment(self, status):
        self.payment_status = status
        self.save(update_fields=['payment_status'])

    def set_payment_cash(self):
        self.payment_source = PaymentSource.CASH
        self.save(update_fields=['payment_source'])

    def set_payment_online(self, reference=None):
        self.payment_source = PaymentSource.ONLINE
        self.payment_reference = reference
        self.save(update_fields=['payment_source', 'payment_reference'])

    def save(self, *args, **kwargs):
        if not self.created:
            self.reference = generate_token(8)
        super().save(*args, **kwargs)
        return self

    def __iter__(self):
        """
        Iterate over the items in the cart and get the items from the database
        """
        return self.lines.all().iterator()

    def partitions(self):
        "Return the cart split into pickup/store groups"
        # TODO(yao): Add partitions for delivery time, address zone
        return partition(self, lambda line: line.item.store, ItemList)

    def get_absolute_url(self):
        return reverse('order:details', kwargs={'token': self.token})

    def is_pending(self):
        return self.status == OrderStatus.PENDING

    def is_open(self):
        statuses = {OrderStatus.UNFULFILLED, OrderStatus.PARTIALLY_FULFILLED}
        return self.status in statuses

    class Meta:
        db_table = "order"
        ordering = ('-updated',)


class OrderLine(BaseModel, ItemLine):

    ID_PREFIX = 'ordl'

    item = models.ForeignKey(Item)
    quantity = models.IntegerField()
    unit_price = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    special_instructions = models.TextField(null=True, blank=True)
    order = models.ForeignKey(Order, related_name='lines', editable=False,
                              on_delete=models.CASCADE)
    data = JSONField(blank=True, default={})

    def get_price_per_item(self):
        return self.unit_price + self.get_options_total()

    __repr__ = sane_repr('item', 'quantity')

    class Meta:
        db_table = "order_line"
