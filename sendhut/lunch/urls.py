from django.conf.urls import url

from .views import (
    CartView, food_detail, cartline_detail, cartline_delete,
    store_page, cart_reload, order_list, order_details, search
)


urlpatterns = [
    url(r'^search/(?P<tag>[a-zA-Z0-9-]+)$', search, name='search'),
    url(r'^cart/reload$', cart_reload, name='cart_reload'),
    url(r'^basket/(?P<line_id>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$',
        cartline_detail, name='cartline_detail'),
    url(r'^basket/(?P<line_id>[a-zA-Z0-9-]+)/delete$',
        cartline_delete, name='cartline_delete'),
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^orders/(?P<ref>[a-zA-Z0-9-]+)$', order_details,
        name='order_details'),
    url(r'^orders/$', order_list, name='order_history'),
    url(r'^store/(?P<slug>[a-zA-Z0-9-]+)/$',
        store_page, name='store_details'),
    url(r'^item/(?P<slug>[a-zA-Z0-9-]+)/$',
        food_detail, name='food_detail')
]
