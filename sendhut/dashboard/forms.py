from django import forms
from .models import Employee


class EmployeeForm(forms.Form):
    email = forms.EmailField()
    # TODO(yao): handle phone number validation and formatting
    phone = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    role = forms.ChoiceField(choices=Employee.ROLES, widget=forms.Select)
