from datetime import datetime

from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.urls import reverse

from sendhut import utils
from sendhut.lunch.models import Item, Order
from .models import Employee, Company, Invite, Allowance
from .forms import EmployeeForm, AllowanceForm
from sendhut.dashboard import emails


def home(request):
    template = 'dashboard/home.html'
    context = {
        'page_title': 'Dashboard',
    }
    return render(request, template, context)


def order_list(request):
    template = 'dashboard/order_list.html'
    context = {
        'page_title': 'Orders',
        'items': Order.objects.all()
    }
    return render(request, template, context)


def employee_list(request):
    company = request.user.company
    template = 'dashboard/employee_list.html'
    context = {
        'page_title': 'Employees',
        'employees': {
            'joined': Employee.objects.filter(company=company),
            'invited': Invite.objects.filter(company=company)
        }
    }
    return render(request, template, context)


def employee_details(request, employee_id):
    # info, orders, allowances
    # Employee.objects.filter
    pass


class EmployeeCreate(FormView):
    template_name = 'dashboard/object_form.html'
    form_class = EmployeeForm
    success_url = '/business/employees'
    page_title = 'Add Employee'

    def get_form_class(self):
        from functools import partial
        return partial(self.form_class, self.request.user.company)

    def form_valid(self, form):
        # TODO(yao): send sms alert?
        data = form.cleaned_data
        company = self.request.user.company
        token = utils.generate_token()
        email = data['email']
        Invite.objects.create(
            token=token,
            company=company,
            email=email,
            role=data['role'],
            allowance_id=data['allowance']
        )
        url = self.request.build_absolute_uri(reverse('dashboard:join', args=(token,)))
        sender = self.request.user.get_full_name()
        emails.send_invitation(data['email'], sender, url)
        email = data['email']
        messages.success(self.request, 'Invitation sent to {}'.format(email))
        return super().form_valid(form)


def employee_disable(request):
    pass


def employee_import_csv(request):
    pass


def accept_invitation(request, token):
    # TODO(yao): logout current session, redirect user to set password, login
    invite = get_object_or_404(Invite, token=token)
    invite.date_joned = datetime.now()
    invite.save()
    Employee.objects.create(user=invite.user, company=invite.company)
    messages.info(request, 'Welcome! You\'ve been added to the {} organisation'.format(invite.company.name))
    return redirect(reverse('home'))


def allowance_list(request):
    company = request.user.company
    template = 'dashboard/allowance_list.html'
    context = {
        'page_title': 'Allowances',
        'allowances': Allowance.objects.filter(company=company)
    }
    return render(request, template, context)


class AllowanceUpdate(FormView):
    template_name = 'dashboard/allowance_form.html'
    form_class = AllowanceForm
    success_url = '/business/allowances'
    page_title = 'Update Allowance'

    def get_initial(self):
        allowance = Allowance.objects.get(id=self.kwargs['allowance_id'])
        return {
            'name': allowance.name,
            'frequency': allowance.frequency,
            'limit': allowance.limit.amount
        }

    def form_valid(self, form):
        data = form.cleaned_data
        member_ids = map(int, form.data.getlist('employees', []))
        members = Employee.objects.filter(id__in=member_ids)
        allowance_id = self.kwargs['allowance_id']
        allowance = Allowance.objects.filter(id=allowance_id).update(**data)
        allowance = Allowance.objects.get(id=allowance_id)
        allowance.members.set(members)
        messages.success(self.request, 'Allowance updated')
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        allowance_id = self.kwargs['allowance_id']
        context['members'] = Employee.objects.filter(
            company=self.request.user.company,
            allowance_id=allowance_id
        )
        context['employees'] = Employee.objects.filter(company=self.request.user.company)
        return context


class AllowanceCreate(FormView):
    template_name = 'dashboard/allowance_form.html'
    form_class = AllowanceForm
    success_url = '/business/allowances'
    page_title = 'Add Allowance'

    def form_valid(self, form):
        data = form.cleaned_data
        member_ids = map(int, form.data.getlist('employees', []))
        members = Employee.objects.filter(id__in=member_ids)
        allowance = Allowance.objects.create(
            created_by=self.request.user,
            company=self.request.user.company,
            **data
        )
        allowance.members.add(*members)
        messages.success(self.request, 'Allowance created')
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = self.request.user.company.employees.all
        return context


def allowance_delete(request, allowance_id):
    # TODO(yao): unlink allowance from members
    allowance = Allowance.objects.delete()
    messages.info(request, "Allowance deleted")
    return redirect(reverse('allowances'))
