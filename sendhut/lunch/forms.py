from django import forms
from .models import Order


class CheckoutForm(forms.Form):
    delivery_address = forms.CharField(max_length=120)
    delivery_time = forms.ChoiceField(
        choices=((x, x) for x in Order.DELIVERY_TIMES)
    )
    notes = forms.CharField(max_length=300, required=False)
