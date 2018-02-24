from django.conf import settings
from templated_email import send_templated_mail
import logging

from jusibe.core import Jusibe

COMPANY_INVITATION_TEMPLATE = 'dashboard/invitation.email'


# SMS
def send_sms(number, message, sender_alias='Sendhut'):
    sms = Jusibe(settings.JUSIBE_PUBLIC_KEY, settings.JUSIBE_ACCESS_TOKEN)
    return sms.send_message(number, sender_alias, message)


# EMAILS
def send_password_reset(phone, token, url=None):
    print("Sending password reset {} {} {}".format(phone, token, url))


# def send_company_invitation(recipient, sender_name, url):
#     send_templated_mail(
#         template_name=COMPANY_INVITATION_TEMPLATE,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[recipient],
#         context={
#             'url': url,
#             'sender_name': sender_name
#         },
#         create_link=True
#     )
