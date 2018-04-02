"""
TODO(yao): add user notifications settings

- SMS Order Confirmations
  Receive a text message when you place an order

- SMS Delivery Notifications
  Receive text message updates when your order is being delivered

Messages:

- "Today's lunch is from Debonairs! See full menu at ..."
- Thanks! Your order has been placed. We'll text you once it's delivered.

Sign-offs:
- As always, thanks for using Sendhut!
- All the best,
- Thank You

# email types
- welcome.mjml
- spicy.mjml
  - holidays
  - special deals
  - feature release
  - order confirmed

- order invoice

simple.mjml:
- feedback
- reset password
- sorry

"""
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site
from templated_email import send_templated_mail
from django.contrib.staticfiles.storage import staticfiles_storage
from django_rq import enqueue

from jusibe.core import Jusibe

from sendhut import utils
from sendhut.accounts.models import User


WELCOME_TEMPLATE = 'source/accounts/welcome'
PASSWORD_RESET_TEMPLATE = 'source/accounts/password_reset'
CONFIRM_ORDER_TEMPLATE = 'source/orders/confirm_order'
CONFIRM_FULFILLMENT_TEMPLATE = 'source/orders/confirm_fulfillment'


def collect_data_for_email(email, template):
    user = User.objects.get(email=email)
    site = Site.objects.get_current()
    return dict(
        template=template,
        recipient=user,
        protocol='https' if settings.ENABLE_SSL else 'http',
        site_name=site.name,
        domain=site.domain,
        site_url=utils.build_absolute_uri(reverse('home')),
        logo_url=staticfiles_storage.url('images/sendhut-yellow.png'),
        banner_image_url=staticfiles_storage.url('images/banner-burgersushi.jpg')
      )


def _send_email(email, template, context=None):
    ctx = collect_data_for_email(email, template)
    if context:
        ctx.update(context)

    send_templated_mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        context=ctx,
        template_name=template,
        create_link=True)


def _send_sms(phone, message, sender_alias='Sendhut'):
    sms = Jusibe(settings.JUSIBE_PUBLIC_KEY, settings.JUSIBE_ACCESS_TOKEN)
    return sms.send_message(phone, sender_alias, message)


# SMS
def send_phone_verification(phone, code):
    message = """
        Your Sendhut code is {} but you can simply tap on this link to verify
        your number. {}
        """.format(code)
    _send_sms(phone, message)


def send_order_confirmation(email, order, async=True):
    "Receive a text message when you place an order"
    # message = """
    # Thanks for ordering. Your order will be delivered at {} to {}.
    # """.format(order.delivery_time, order.delivery_address)
    # send_sms(phone, message)
    if async:
        return enqueue(_send_email, email, CONFIRM_ORDER_TEMPLATE, {'order': order})

    _send_email(email, CONFIRM_ORDER_TEMPLATE, {'order': order})


# EMAILS
def send_welcome_email(email, async=True):
    ctx = dict(
        store_image_url_1=staticfiles_storage.url('images/rice-dodo.jpeg'),
        store_image_url_2=staticfiles_storage.url('images/burger.jpg'),
        store_image_url_3=staticfiles_storage.url('images/salad.jpg'),
        explore_message='Try our selection of tasty Nigerian dishes, \
        Oven-baked Pizza, Fresh salads, and more.')
    if async:
        return enqueue(_send_email, email, WELCOME_TEMPLATE, ctx)

    _send_email(email, WELCOME_TEMPLATE, ctx)


def send_password_reset(email, token, async=True):
    url = utils.build_absolute_uri(
        reverse('accounts:password_reset_confirm', args=(token,)))
    ctx = {'password_reset_url': url}
    if async:
        return enqueue(_send_email, email, PASSWORD_RESET_TEMPLATE, ctx)

    return _send_email(email, PASSWORD_RESET_TEMPLATE, ctx)
