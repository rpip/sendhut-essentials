from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

from sendhut.cart.models import Cart
from sendhut.lunch.models import Store
from sendhut.checkout.models import Order
from . import payments


def home(request):
    if settings.BETA_MODE:
        messages.info(request, settings.BETA_MESSAGE)

    context = {
        'page_title': 'Home',
        'restaurants': Store.featured.all()
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
