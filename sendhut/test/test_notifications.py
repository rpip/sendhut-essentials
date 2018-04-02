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
            email='yao.adzaku@gmail.com',
            phone='08169567693'
        )
        create_lagos_stores(2)
        order = OrderFactory.create(user=user)
        create_orderlines(order)

    @override_settings(EMAIL_BACKEND='django_mailgun.MailgunBackend')
    def test_send_emails(self):
        ctx = dict(
            store_image_url_1='http://demo.tutorialzine.com/2017/02/images/pizza.jpg',
            store_image_url_2='http://demo.tutorialzine.com/2017/02/images/cake.jpg',
            store_image_url_3='http://demo.tutorialzine.com/2017/02/images/salad.jpg',
            order_now_message='Try our selection of Oven-baked Pizza, Fresh Salads, and Homemade Cake.'
        )
        for user in User.objects.all():
            order = user.orders.first()
            notifications.send_welcome_email(user.email, ctx)
            notifications.send_password_reset(user.email, 'jh5f5678')
            notifications.send_order_confirmation(user.phone, user.email, order)

    @override_settings(EMAIL_BACKEND='django_mailgun.MailgunBackend')
    def test_send_sms(self):
        pass
