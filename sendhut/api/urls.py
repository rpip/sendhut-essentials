from django.conf.urls import url, include

from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register('users', views.UserViewSet)
router.register('stores', views.StoreViewSet)
router.register('items', views.ItemViewSet)
router.register('orders', views.OrderViewSet)
router.register('gifts', views.GiveAwayViewSet)
router.register('coupons', views.CouponViewSet)


urlpatterns = [
    url('^', include(router.urls))
]
