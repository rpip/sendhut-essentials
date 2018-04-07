from django import forms


class GroupOrderForm(forms.Form):
    limit = forms.FloatField(required=False)
    store = forms.CharField()
