from django import forms


class CheckoutForm(forms.Form):
    delivery_point = forms.CharField(max_length=6, required=False)
    address = forms.CharField(max_length=120)
    time = forms.CharField(max_length=30)
    date = forms.CharField(max_length=30)
    notes = forms.CharField(max_length=300, required=False)
    cash = forms.BooleanField(required=False)

    # def clean_address(self):
    #     address = self.cleaned_data['address']
    #     delivery_point = self.cleaned_data['delivery_point']
    #     if address:
    #         return Address.objects.create(address=address)

    #     # if in giveaway and giveaway has addresses
    #     if delivery_point:
    #         return Address.objects.get(id=delivery_point)
