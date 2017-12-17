from django import forms
from .models import Employee


class EmployeeForm(forms.Form):
    email = forms.EmailField()
    phone = forms.CharField(max_length=100, widget=forms.HiddenInput())
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    role = forms.ChoiceField(choices=Employee.ROLES, widget=forms.Select)
