"""
Payment: add payment card / enter promo code
set time: ASAP | scheduled (pick a date and time)
Address: Add / change (Address has delivery instructions)
Tips
service fee: message(This x% service helps us operate Sendhut)

# NOTES
DoorDash charges 11%
"""
from django.utils.translation import pgettext_lazy


class PaymentStatus:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    REFUNDED = 'refunded'
    FAILED = 'ERROR'

    CHOICES = [
        (PENDING, pgettext_lazy('payment status', 'Waiting for confirmation')),
        (CONFIRMED, pgettext_lazy('payment status', 'Confirmed')),
        (REFUNDED, pgettext_lazy('payment status', 'Refunded')),
        (FAILED, pgettext_lazy('payment status', 'Rejected')),
    ]


class PaymentSource:
    # TODO(yao): add user flag to mark users who can do CASH delivery

    CASH = 'cash'
    ONLINE = 'online'

    CHOICES = (
        (CASH, 'Cash'),
        (ONLINE, 'Online')
    )


class OrderStatus:
    PENDING = 'pending'
    UNFULFILLED = 'unfulfilled'
    PARTIALLY_FULFILLED = 'partially fulfilled'
    FULFILLED = 'fulfilled'
    CANCELED = 'canceled'
    PROCESSING = 'processing'
    TRANSIT = 'transit'

    CHOICES = [
        (PENDING, pgettext_lazy(
            'Status for a fully editable, not unconfirmed order created by ',
            'Draft')),
        (UNFULFILLED, pgettext_lazy(
            'Status for an order with any items marked as fulfilled',
            'Unfulfilled')),
        (PARTIALLY_FULFILLED, pgettext_lazy(
            'Status for an order with some items marked as fulfilled',
            'Partially fulfilled')),
        (FULFILLED, pgettext_lazy(
            'Status for an order with all items marked as fulfilled',
            'Fulfilled')),
        (CANCELED, pgettext_lazy(
            'Status for a permanently canceled order',
            'Canceled')),
        (PROCESSING, pgettext_lazy(
            'Status for a permanently canceled order',
            'Canceled')),
        (PROCESSING, pgettext_lazy(
            'Status for an order confirmed and being processed by Sendhut',
            'Processing')),
        (TRANSIT, pgettext_lazy(
            'Status for an order being delivered',
            'Transit')),
    ]
