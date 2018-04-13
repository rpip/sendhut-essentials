from django import forms
from .models import Order


class CheckoutForm(forms.Form):
    address = forms.CharField(max_length=120)
    time = forms.ChoiceField(
        choices=((x, x) for x in Order.DELIVERY_TIMES))
    notes = forms.CharField(max_length=300, required=False)
    cash = forms.BooleanField(required=False)
