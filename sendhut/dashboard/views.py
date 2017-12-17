from django.views import View
from django.views.generic.edit import FormView
from sendhut.lunch.models import Item, Order
from .models import Employee, Company
from .forms import EmployeeForm
from django.shortcuts import render


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
    # returns two columns: joined, invited
    template = 'dashboard/order_list.html'
    company_id = request.user.company.id
    context = {
        'employees': Employee.objects.filter(company_id=company_id)
    }
    return render(request, template, context)


def employee_details(request):
    # info, orders, allowances
    pass


class EmployeeCreate(FormView):
    template_name = 'dashboard/employee_form.html'
    form_class = EmployeeForm
    success_url = '/business/employees'

    def form_valid(self, form):
        # TODO(yao): create and attach associated user
        # TODO(yao): attach associated company
        # invite token,
        return super().form_valid(form)


def employee_disable(request):
    pass


def employee_import_csv(request):
    pass


class AllowanceView(View):
    pass
