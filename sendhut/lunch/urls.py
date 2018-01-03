from django.conf.urls import url
from .views import (
    FoodDetailView, CartView, CartLineDetailView,
    CartLineDeleteView, DeliveryTimeView, CheckoutView,
    restaurant_menu, cart_reload, cart_summary,
    list_orders
)


urlpatterns = [
    url(r'^cart/(?P<uuid>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$',
        CartLineDetailView.as_view(), name='cartline_detail'),
    url(r'^cart/(?P<uuid>[a-zA-Z0-9-]+)/delete$',
        CartLineDeleteView.as_view(), name='cartline_delete'),
    url(r'^cart/delivery-time$', DeliveryTimeView.as_view(), name='cart_delivery'),
    url(r'^cart/reload$', cart_reload, name='cart_reload'),
    url(r'^cart/summary$', cart_summary, name='cart_summary'),
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^checkout/$', CheckoutView.as_view(), name='checkout'),
    url(r'^orders/$', list_orders, name='order_history'),
    url(r'^restaurant/(?P<slug>[a-zA-Z0-9-]+)/$',
        restaurant_menu, name='restaurant_menu'),
    url(r'^(?P<vendor>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$',
        FoodDetailView.as_view(), name='food_detail'),
]
