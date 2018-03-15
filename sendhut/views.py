from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

from sendhut.cart import Cart
from sendhut.lunch.models import Vendor, Order
from sendhut.lunch.views import GroupOrder
from . import payments


def home(request):
    messages.info(request, settings.WELCOME_MESSAGE)
    context = {
        'page_title': 'Home',
        'restaurants': Vendor.featured.all()
    }
    return render(request, 'home.html', context)


def about(request):
    return render(request, 'about.html', {'page_title': 'About Us'})


def faqs(request):
    return render(request, 'faqs.html', {'page_title': 'FAQs'})


def privacy_terms(request):
    return render(request, 'privacy_terms.html', {
        'page_title': 'Privacy & Terms'
    })


def payment_callback(request):
    # TODO(yao): alert slack/sms/email channel about payment status
    reference = request.GET['reference']
    if payments.verify_transaction(reference):
        order = Order.objects.get(reference=reference)
        order.payment = Order.CONFIRMED
        order.payment_source = Order.ONLINE
        order.save()
        success_message = "Payment confirmed. We'll deliver your lunch at {}".format(order.delivery_time)
        messages.info(request, success_message)
        Cart(request).clear()
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
