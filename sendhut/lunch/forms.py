from django import forms
from .models import Order, Vendor, GroupCart
from django.forms import ModelForm


class CheckoutForm(forms.Form):
    delivery_address = forms.CharField(max_length=120)
    delivery_time = forms.ChoiceField(
        choices=((x, x) for x in Order.DELIVERY_TIMES)
    )
    notes = forms.CharField(max_length=300, required=False)
    cash_delivery = forms.BooleanField(required=False)


class VendorSignupForm(ModelForm):
    # number of locations
    # type of cuisine
    # estimated weekly to-go orders
    # do you currently offer delivery
    class Meta:
        model = Vendor
        fields = ['manager_name', 'phone', 'email', 'name']
        labels = {
            "manager_name": "Name",
            "name": "Business Name"
        }
