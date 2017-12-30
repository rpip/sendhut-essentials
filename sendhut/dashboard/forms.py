from django import forms
from .models import Employee, Allowance


class EmployeeForm(forms.Form):
    email = forms.EmailField()
    allowance = forms.ChoiceField(widget=forms.Select)
    role = forms.ChoiceField(choices=Employee.ROLES, widget=forms.Select)

    def __init__(self, company=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            choices = [(o.id, str(o)) for o in company.allowances.all()]
            self.fields['allowance'] = forms.ChoiceField(choices=choices)

    def clean_allowance(self):
        return self.data['allowance']


class AllowanceForm(forms.Form):
    name = forms.CharField(max_length=60)
    frequency = forms.ChoiceField(
        choices=Allowance.FREQUENCY,
        widget=forms.Select
    )
    limit = forms.DecimalField()
