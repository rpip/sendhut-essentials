from django.urls import reverse
from django.conf import settings
from paystackapi.paystack import Paystack


paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)


def init(reference, amount, email):
    # TODO(yao): confirm Paystack max amount, why 33578.00, appears as 335.78
    return paystack.transaction.initialize(
        reference=reference,
        amount=amount,
        email=email,
        callback_url=reverse('checkout:ck')
    )


def verify_transaction(reference):
    response = paystack.transaction.verify(reference)
    return response['status']
