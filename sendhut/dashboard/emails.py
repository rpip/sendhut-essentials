from django.conf import settings
from templated_email import send_templated_mail


INVITATION_TEMPLATE = 'dashboard/invitation.email'


def send_invitation(recipient, sender_name, url):
    send_templated_mail(
        template_name=INVITATION_TEMPLATE,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        context={
            'url': url,
            'sender_name': sender_name
        },
        create_link=True
    )
