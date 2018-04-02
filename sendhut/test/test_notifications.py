from django.test import TestCase, override_settings

from sendhut import notifications
from sendhut.accounts.models import User
from sendhut.lunch.management.commands.load_menus import create_lagos_stores
from sendhut.factory import (
    UserFactory, OrderFactory, ItemFactory,
    create_orderlines
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

    @override_settings(EMAIL_BACKEND='django_mailgun.MailgunBackend')
    def test_send_emails(self):
        user = User.objects.get(email='yao@sendhut.com')
        order = user.orders.first()
        notifications.send_welcome_email(user.email, False)
        notifications.send_password_reset(user.email, 'jh5f5678', False)
        notifications.send_order_confirmation(user.email, order, False)

    @override_settings(EMAIL_BACKEND='django_mailgun.MailgunBackend')
    def test_send_sms(self):
        pass
