from django.conf.urls import url
from .views import (
    FoodDetailView, CartView,
    CheckOutView, order_history, CartLineDetailView,
    CartLineDeleteView, restaurant_menu
)


urlpatterns = [
    url(r'^cart/(?P<hash>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$',
        CartLineDetailView.as_view(), name='cartline_detail'),
    url(r'^cart/(?P<hash>[a-zA-Z0-9-]+)/$',
        CartLineDeleteView.as_view(), name='cartline_delete'),
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^checkout/$', CheckOutView.as_view(), name='checkout'),
    url(r'^orders/$', order_history, name='order_history'),
    url(r'^restaurant/(?P<slug>[a-zA-Z0-9-]+)/$',
        restaurant_menu, name='restaurant_menu'),
    url(r'^(?P<vendor>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$',
        FoodDetailView.as_view(), name='food_detail'),
]
