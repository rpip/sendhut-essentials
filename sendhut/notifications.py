"""
TODO(yao): add user notifications settings

- SMS Order Confirmations
  Receive a text message when you place an order

- SMS Delivery Notifications
  Receive text message updates when your order is being delivered

Messages:

- "Today's lunch is from Debonairs! See full menu at ..."
- Thanks! Your order has been placed. We'll text you once it's delivered.
"""
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site
from templated_email import send_templated_mail

from jusibe.core import Jusibe

from sendhut import utils
from sendhut.accounts.models import User
from sendhut.api.serializers import UserSerializer


WELCOME_TEMPLATE = 'source/accounts/welcome'
PASSWORD_RESET_TEMPLATE = 'source/accounts/password_reset'
ORDER_CONFIRMED_TEMPLATE = 'source/orders/order_confirmed'
GROUP_ORDER_CONFIRMED_TEMPLATE = 'source/orders/order_confirmed'


def collect_data_for_email(email, template):
    user = User.objects.filter(email=email).first()
    user = UserSerializer(instance=user).data if user else {'email': email}
    return {'template': template, 'recipient': user}


def _send_email(email, template, context=None):
    email_data = collect_data_for_email(email, template)
    site = Site.objects.get_current()
    ctx = dict(
        email_data,
        protocol='https' if settings.ENABLE_SSL else 'http',
        site_name=site.name,
        domain=site.domain,
        url=utils.build_absolute_uri(reverse('home'))
    )
    if context:
        ctx.update(context)

    send_templated_mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        context=ctx,
        template_name=template,
        create_link=True)


def _send_sms(number, message, sender_alias='Sendhut'):
    sms = Jusibe(settings.JUSIBE_PUBLIC_KEY, settings.JUSIBE_ACCESS_TOKEN)
    return sms.send_message(number, sender_alias, message)


# SMS
def send_phone_verification(number, code):
    message = """
        Your Sendhut code is {} but you can simply tap on this link to verify
        your number. {}
        """.format(code)
    _send_sms(number, message)


def send_order_confirmation(number, order):
    "Receive a text message when you place an order"
    message = """
    Thanks for ordering. Your order will be delivered at {} to {}.
    """.format(order.delivery_time, order.delivery_address)
    _send_sms(number, message)


def send_delivery_update(phone):
    "Receive text message updates when your order is being delivered"
    pass


# EMAILS
def send_welcome_note(email):
    _send_email(email, WELCOME_TEMPLATE)


def send_group_order_confirmation(email, order):
    _send_email(email, GROUP_ORDER_CONFIRMED_TEMPLATE)


def send_password_reset(email, token):
    url = utils.build_absolute_uri(
        reverse('accounts:password_reset_confirm', args=(token,)))
    _send_email(email, PASSWORD_RESET_TEMPLATE, {'password_reset_url': url})
