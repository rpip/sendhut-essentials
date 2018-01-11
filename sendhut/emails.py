from django.conf import settings
from templated_email import send_templated_mail


COMPANY_INVITATION_TEMPLATE = 'dashboard/invitation.email'

BUSINESS_SIGNUP_TEMPLATE = 'dashboard/signup.email'


def send_company_invitation(recipient, sender_name, url):
    send_templated_mail(
        template_name=COMPANY_INVITATION_TEMPLATE,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        context={
            'url': url,
            'sender_name': sender_name
        },
        create_link=True
    )


def alert_business_signup(email, company_name):
    send_templated_mail(
        template_name=BUSINESS_SIGNUP_TEMPLATE,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.SENDHUT_EMAIL],
        context={
            'company': company_name,
            'email': email
        },
        create_link=True
    )
