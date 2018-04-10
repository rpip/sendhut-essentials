from django.conf.urls import url

from .views import cart_summary, checkout, payment_webhook, payment_callback


urlpatterns = [
    url(r'^$', cart_summary, name='summary'),
    url(r'^checkout/$', checkout, name='getit'),
    # instant payment notification
    url(r'^payments/ipn$', payment_webhook, name='ipn'),
    # payment transaction callback
    url(r'^payments/ck$', payment_callback, name='ck'),
]
