from .models import Partner
from django.forms import ModelForm


class PartnerSignupForm(ModelForm):
    # number of locations
    # type of cuisine
    # estimated weekly to-go orders
    # do you currently offer delivery
    class Meta:
        # TODO(yao): map to Partner/Merchant
        model = Partner
        fields = ['name', 'business_name', 'phone', 'email', 'has_fleets']
        labels = {
            'has_fleets': 'Do you provide your own delivery drivers?'
        }
