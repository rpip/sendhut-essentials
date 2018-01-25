from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page

from sendhut.lunch.models import Vendor, Payment, Order
from . import payments


@cache_page(60 * 60)
def home(request):
    messages.info(request, settings.WELCOME_MESSAGE)
    context = {
        'page_title': 'Home',
        'restaurants': Vendor.objects.all()[:6]
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
    # TODO(yao): difference between txref and reference
    # payments/ck?trxref=a0200d217c436d44&reference=a0200d217c436d44
    # TODO(yao): alert slack/sms/email channel about payment status
    # txref = request.GET['txref']
    reference = request.GET['reference']
    if payments.verify_transaction(reference):
        payment = Payment.objects.get(reference=reference)
        payment.status = Payment.CONFIRMED
        payment.save()
        order_ref = payment.metadata['order_ref']
        order = Order.objects.get(reference=order_ref)
        success_message = "Payment confirmed. We'll deliver your lunch at {}".format(order.delivery_time)
        messages.info(request, success_message)
        return redirect('home')
        # TODO(yao): clear cart after payment confirmed
        # Cart(request).clear()
    else:
        error_message = "Payment failed. We can arrange for you to pay when the \
        meal arrives. Let us know now!"
        # TODO(yao): reach out to customers whose payment failed
        messages.error(request, success_message)
        return redirect('lunch:cart_summary')


def payment_webhook(request):
    pass
