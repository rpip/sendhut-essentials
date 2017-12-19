from django import forms
from .models import Employee, Allowance


class EmployeeForm(forms.Form):
    email = forms.EmailField()
    # TODO(yao): handle phone number validation and formatting
    phone = forms.CharField(max_length=32)
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    role = forms.ChoiceField(choices=Employee.ROLES, widget=forms.Select)


class AllowanceForm(forms.Form):
    name = forms.CharField(max_length=32)
    frequency = forms.ChoiceField(
        choices=Allowance.FREQUENCY,
        widget=forms.Select
    )
    limit = forms.DecimalField()
