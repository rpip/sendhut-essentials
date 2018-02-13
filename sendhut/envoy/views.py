from django.views.generic.edit import FormView
from django.contrib import messages
from .forms import MerchantForm


class BusinessView(FormView):
    template_name = 'envoy/business.html'
    form_class = MerchantForm
    page_title = 'Deliver with Sendhut'
    success_url = '/business/'

    def form_valid(self, form):
        messages.info(self.request, "We'll reach out shortly. Than you")
        Merchant.objects.create()
        return super().form_valid(form)
