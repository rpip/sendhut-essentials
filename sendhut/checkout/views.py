from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from sendhut.cart.utils import get_cart_data
from sendhut import payments, notifications
from .models import Order
from . import PaymentStatus
from .utils import Checkout

from .forms import CheckoutForm


@login_required
def cart_summary(request):
    # TODO(yao): group order summary
    form = CheckoutForm(data=request.POST)
    context = get_cart_data(request.cart)
    context['form'] = form
    return render(request, 'checkout/cart_summary.html', context)


@login_required
def checkout(request):
    form = CheckoutForm(data=request.POST)
    cart = request.cart
    if not(form.is_valid()):
        messages.error(request, "Please complete the delivery form to proceed")
        context = get_cart_data(cart)
        return render(request, 'checkout/cart_summary.html', context)

    cash_delivery = form.cleaned_data.pop('cash_delivery')
    cart = request.cart
    user = request.user
    checkout = Checkout(cart, user)
    order = checkout.create_order(**form.cleaned_data)
    # TODO(yao): also notify group cart owner participants
    confirm_msg = "Order submitted for processing. reference {}".format(order.reference)
    messages.info(request, confirm_msg)
    notifications.send_order_confirmation(user.email, order)

    if not(cash_delivery):
        from sendhut.utils import quantize
        amount = checkout.get_total()
        response = payments.init(order.reference, quantize(amount.amount), request.user.email)
        if response['status']:
            return redirect(response['data']['authorization_url'])
        else:
            # TODO(yao): what to do if payment fails
            order.update_payment(PaymentStatus.FAILED)
            messages.error(request, "Payment failed. Please try again")

    return redirect('home')


def payment_callback(request):
    # TODO(yao): alert slack/sms/email channel about payment status
    reference = request.GET['reference']
    if payments.verify_transaction(reference):
        order = Order.objects.get(reference=reference)
        order.update_payment(PaymentStatus.CONFIRMED)
        success_msg = "Payment confirmed. We'll deliver your lunch at {}".format(order.time)
        messages.info(request, success_msg)
        # TODO(yao): delete cart ?
        # TODO(yao): end group order session, lock cart
        return redirect('home')
    else:
        error_message = "Payment failed. We can arrange for you to pay when the \
        meal arrives. Let us know now!"
        # TODO(yao): reach out to customers whose payment failed
        messages.error(request, error_message)
        return redirect('lunch:cart_summary')


def payment_webhook(request):
    pass
