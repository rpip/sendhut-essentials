from django import forms


class CheckoutForm(forms.Form):
    address = forms.CharField(max_length=120)
    time = forms.CharField(max_length=30)
    date = forms.CharField(max_length=30)
    notes = forms.CharField(max_length=300, required=False)
    cash = forms.BooleanField(required=False)
