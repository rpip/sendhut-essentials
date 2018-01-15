from django.urls import reverse
from django.conf import settings
from paystackapi.paystack import Paystack

from sendhut.lunch.models import Payment
from . import utils

paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)


def initialize_payment(order, amount, email):
    # TODO(yao): confirm Paystack max amount, why 33578.00, appears as 335.78
    # TODO(yao): how to use localhost callback_url
    reference = utils.generate_token()
    meta = {'order_ref': order.reference}
    payment = Payment.objects.create(reference=reference, metadata=meta)
    order.payment = payment
    order.save()
    return paystack.transaction.initialize(
        reference=reference,
        amount=amount,
        email=email,
        callback_url=reverse('lunch:cart_summary')
    )


def verify_transaction(reference):
    response = paystack.transaction.verify(reference)
    return response['status'] == 'success'
