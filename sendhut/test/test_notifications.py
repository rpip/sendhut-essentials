from django.test import TestCase, override_settings

from sendhut import notifications
from sendhut.factory import (
    UserFactory, OrderFactory, GroupOrderFactory, MemberFactory,
    create_orderlines
)
from sendhut.accounts.models import User
from sendhut.management.commands.load_menus import create_lagos_stores
from sendhut.stores.models import Item, Store


class NotificationsTestClass(TestCase):

    def setUp(self):
        # TODO(yao): create group order
        user = UserFactory.create(
            first_name='Yao',
            last_name='Adzaku',
            email='yao@sendhut.com',
            phone='08169567693'
        )
        create_lagos_stores(3)
        order = OrderFactory.create(user=user)
        create_orderlines(order, Item.objects.all()[:5])

        group_order = OrderFactory.create(user=user)
        create_group_order(user, group_order)

    @override_settings(EMAIL_BACKEND='django_mailgun.MailgunBackend')
    def test_send_emails(self):
        user = User.objects.get(email='yao@sendhut.com')
        notifications.send_welcome_email(user.email, False)
        notifications.send_password_reset(user.email, 'jh5f5678', False)
        for order in user.orders.all():
            notifications.send_order_confirmation(user, order, False)


def create_group_order(user, order):
    store = Store.objects.first()
    group_order = GroupOrderFactory.create(user=user, store=store)
    order.group_order = group_order
    order.save()
    MemberFactory.create_batch(4, group_order=group_order)
