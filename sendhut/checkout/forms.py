from django import forms
from datetime import datetime
from .models import Order


class CheckoutForm(forms.Form):
    address = forms.CharField(max_length=120)
    time = forms.ChoiceField(
        choices=((x, x) for x in Order.DELIVERY_TIMES))
    notes = forms.CharField(max_length=300, required=False)
    cash_delivery = forms.BooleanField(required=False)

    def clean_time(self):
        delivery_time = self.cleaned_data['time']
        hour, minute = delivery_time.split(':')
        return datetime.today().replace(hour=int(hour), minute=int(minute))
