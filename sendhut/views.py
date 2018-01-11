from django.conf import settings
from django.contrib import messages
from django.shortcuts import render

from sendhut.lunch.models import Partner
from sendhut.dashboard.forms import BusinessSignupForm


def home(request):
    messages.info(request, settings.WELCOME_MESSAGE)
    context = {
        'page_title': 'Home',
        'restaurants': Partner.objects.all()[:6],
        'business_signup_form': BusinessSignupForm()
    }
    return render(request, 'home.html', context)


def about(request):
    return render(request, 'about.html', {'page_title': 'About Us'})


def faqs(request):
    return render(request, 'faqs.html', {'page_title': 'FAQs'})


def privacy_terms(request):
    return render(request, 'privacy_terms.html', {'page_title': 'Privacy & Terms'})
