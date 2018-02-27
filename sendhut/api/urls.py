from django.conf.urls import url, include

from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register('users', views.UserViewSet)
router.register('vendors', views.VendorViewSet)
router.register('items', views.ItemViewSet)
router.register('orders', views.OrderViewSet)
router.register('carts', views.GroupCartViewSet)


urlpatterns = [
    url('^', include(router.urls))
]