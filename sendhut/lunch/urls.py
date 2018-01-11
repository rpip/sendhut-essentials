from django.conf.urls import url
from .views import (
    CartView, CheckoutView,
    food_detail, cartline_detail, cartline_delete, vendor_page,
    cart_reload, cart_summary, order_list, order_details,
    search
)


urlpatterns = [
    url(r'^(?P<tag>[a-zA-Z0-9-]+)$', search, name='search'),
    url(r'^cart/(?P<line_id>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$',
        cartline_detail, name='cartline_detail'),
    url(r'^cart/(?P<line_id>[a-zA-Z0-9-]+)/delete$',
        cartline_delete, name='cartline_delete'),
    url(r'^cart/reload$', cart_reload, name='cart_reload'),
    url(r'^cart/summary$', cart_summary, name='cart_summary'),
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^checkout/$', CheckoutView.as_view(), name='checkout'),
    url(r'^orders/(?P<reference>[a-zA-Z0-9-]+)$', order_details,
        name='order_details'),
    url(r'^orders/$', order_list, name='order_history'),
    url(r'^vendor/(?P<slug>[a-zA-Z0-9-]+)/$',
        vendor_page, name='restaurant_menu'),
    url(r'^item/(?P<slug>[a-zA-Z0-9-]+)/$',
        food_detail, name='food_detail')
]
