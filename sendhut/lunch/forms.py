from django import forms
from .models import Order, Store, GroupCart, Partner
from django.forms import ModelForm
from datetime import datetime


class CheckoutForm(forms.Form):
    delivery_address = forms.CharField(max_length=120)
    delivery_time = forms.ChoiceField(
        choices=((x, x) for x in Order.DELIVERY_TIMES)
    )
    notes = forms.CharField(max_length=300, required=False)
    cash_delivery = forms.BooleanField(required=False)

    def clean_delivery_time(self):
        delivery_time = self.cleaned_data['delivery_time']
        hour, minute = delivery_time.split(':')
        return datetime.today().replace(hour=int(hour), minute=int(minute))


class GroupOrderForm(forms.Form):
    limit = forms.FloatField(required=False)
    store = forms.CharField()


class PartnerSignupForm(ModelForm):
    # number of locations
    # type of cuisine
    # estimated weekly to-go orders
    # do you currently offer delivery
    class Meta:
        # TODO(yao): map to Partner/Merchant
        model = Partner
        fields = ['name', 'business_name', 'phone', 'email']
