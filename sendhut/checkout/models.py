from datetime import datetime

from django.urls import reverse
from django.conf import settings
from django.db import models
from jsonfield import JSONField
from djmoney.models.fields import MoneyField

from sendhut.db import BaseModel
from sendhut.lunch.models import Item
from sendhut.utils import generate_token, sane_repr
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


class Order(BaseModel):

    DELIVERY_TIMES = (
        '11:30',
        '12:00',
        '12:30',
        '1:00',
        '1:30',
        '2:00',
        '2:30'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders')
    reference = models.CharField(max_length=8, unique=True)
    # TODO(yao): Add types of orders:
    #   Orders that have already been placed:
    #   Orders that are placed and paid for
    #   Manual payment and order:
    time = models.DateTimeField(default=datetime.now)
    address = models.CharField(max_length=120)
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
    # group_order = models.OneToOneField('GroupOrder',
    # related_name='order', null=True, blank=True)

    def update_payment(self, status):
        self.payment_status = status
        self.save(update_fields=['payment_status'])

    def save(self, *args, **kwargs):
        if not self.created:
            self.reference = generate_token(8)
        super().save(*args, **kwargs)
        return self

    def get_total(self):
        return sum(line.get_total() for line in self.lines.all())

    @classmethod
    def get_today_delivery_schedules(cls):
        schedule = []
        for time in cls.DELIVERY_TIMES:
            hour, minute = time.split(':')
            schedule.append(datetime.today().replace(hour=int(hour), minute=int(minute)))
        return schedule

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


class OrderLine(BaseModel):

    item = models.ForeignKey(Item)
    quantity = models.IntegerField()
    unit_price = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    special_instructions = models.TextField(null=True, blank=True)
    order = models.ForeignKey(Order, related_name='lines', editable=False,
                              on_delete=models.CASCADE)
    data = JSONField(blank=True, default={})

    def get_total(self):
        return self.unit_price * self.quantity * self.get_options_total()

    def get_options_total(self):
        pass

    @property
    def store(self):
        return self.item.menu.store

    __repr__ = sane_repr('item', 'quantity')

    class Meta:
        db_table = "order_line"
