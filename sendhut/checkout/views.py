from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from sendhut.cart.utils import get_cart_data
from sendhut import notifications
from .models import Order
from .utils import Checkout, do_checkout_cleanup

from .forms import CheckoutForm


def cart_summary(request):
    # TODO(yao): group order summary
    form = CheckoutForm(data=request.POST)
    context = get_cart_data(request.cart, request.group_member)
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

    cart = request.cart
    user = request.user
    checkout = Checkout(cart, user)
    order = checkout.create_order(**form.cleaned_data)
    # TODO(yao): also notify group cart owner participants
    confirm_msg = "Order submitted for processing. reference {}".format(order.reference)
    messages.info(request, confirm_msg)
    notifications.send_order_confirmation(user, order)

    response = redirect('home')
    do_checkout_cleanup(response, order)
    return response


def payment_webhook(request):
    # TODO(yao): handle payment webhooks
    pass
