from django import forms
from .models import Order
from djmoney.forms import MoneyField


class CheckoutForm(forms.Form):
    delivery_address = forms.CharField(max_length=120)
    delivery_time = forms.ChoiceField(
        choices=((x, x) for x in Order.DELIVERY_TIMES)
    )
    notes = forms.CharField(max_length=300, required=False)
    cash_delivery = forms.BooleanField(required=False)


class GroupOrderForm(forms.Form):

    members_help_text = """Type or paste email addresses or phone numbers,
    separated by commas. Not required
    """
    monetary_limit = forms.DecimalField(
        label='Budget limit',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'You can set a budget limit here'}
    ))
    # members = forms.CharField(
    #     required=False,
    #     label='Participants',
    #     widget=forms.Textarea(attrs={'placeholder': members_help_text}))
