from datetime import datetime

from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
from django.core.mail import send_mail
from django.urls import reverse

from sendhut import utils
from sendhut.accounts.models import User
from sendhut.lunch.models import Item, Order
from .models import Employee, Company, Invite
from .forms import EmployeeForm


def home(request):
    template = 'dashboard/home.html'
    context = {
        'page_title': 'Dashboard',
        'items': Item.objects.all()[:3]
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


def employee_details(request):
    # info, orders, allowances
    pass


class EmployeeCreate(FormView):
    template_name = 'dashboard/employee_form.html'
    form_class = EmployeeForm
    success_url = '/business/employees'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Employee'
        return context

    def form_valid(self, form):
        # TODO(yao): send invitation email/sms
        # SEE https://simpleisbetterthancomplex.com/tutorial/2017/05/27/how-to-configure-mailgun-to-send-emails-in-a-django-app.html
        data = form.cleaned_data
        _role = data.pop('role')
        company = self.request.user.company
        token = utils.generate_token()
        username = '{}-{}'.format(slugify(company.name), token)
        user = User.objects.create(username=username, **data)
        Invite.objects.create(token=token, company=company, user=user)
        url = self.request.build_absolute_uri(reverse('dashboard:join', args=(token,)))
        subject = 'Lunch - {}'.format(self.request.user.get_full_name())
        body = 'Join me for lunch here {}'.format(url)
        send_mail(subject, body, 'yao@sendhut.com', [data['email'], ])
        messages.success(self.request, 'Invitation sent to {}'.format(user.get_full_name()))
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


class AllowanceView(View):
    # list allowances
    # create, delete, update allowance
    # add employees
    # remove employees
    pass
