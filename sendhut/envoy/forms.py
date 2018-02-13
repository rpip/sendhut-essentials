from django.forms import ModelForm

from .models import Merchant


class MerchantForm(ModelForm):

    class Meta:
        model = Merchant
        fields = ['name', 'phone_number', 'email', 'business_name']
