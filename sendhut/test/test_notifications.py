from django.test import TestCase, override_settings

from sendhut import notifications
from sendhut.accounts.models import User
from sendhut.lunch.management.commands.load_menus import create_lagos_stores
from sendhut.lunch.models import GroupCart, GroupCartMember, Store
from sendhut.factory import (
    UserFactory, OrderFactory, ItemFactory, GroupCartFactory,
    GroupCartMemberFactory, create_orderlines
)


class NotificationsTestClass(TestCase):

    def setUp(self):
        # TODO(yao): create group order
        user = UserFactory.create(
            first_name='Yao',
            last_name='Adzaku',
            email='yao@sendhut.com',
            phone='08169567693'
        )
        create_lagos_stores(2)
        order = OrderFactory.create(user=user)
        create_orderlines(order)

        group_order = OrderFactory.create(user=user)
        create_group_order(user, group_order)

    @override_settings(EMAIL_BACKEND='django_mailgun.MailgunBackend')
    def test_send_emails(self):
        user = User.objects.get(email='yao@sendhut.com')
        notifications.send_welcome_email(user.email, False)
        notifications.send_password_reset(user.email, 'jh5f5678', False)
        for order in user.orders.all():
            notifications.send_order_confirmation(user.email, order, False)


def create_group_order(user, order):
    store = Store.objects.first()
    group_cart = GroupCartFactory.create(owner=user, store=store)
    order.group_cart = group_cart
    order.save()
    GroupCartMemberFactory.create_batch(4, group_cart=group_cart)
