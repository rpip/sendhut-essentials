from rest_framework import viewsets

from sendhut.accounts.models import User, Address
from sendhut.stores.models import Store, Item
from sendhut.checkout.models import Order
from sendhut..models import GiveAway, Coupon


from . import serializers


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AddressSerializer
    queryset = Address.objects.all()


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StoreSerializer
    queryset = Store.objects.all()
    lookup_field = 'slug'


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ItemSerializer
    queryset = Item.objects.all()
    lookup_field = 'slug'


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all()


class GiveAwayViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GiveAwaySerializer
    queryset = GiveAway.objects.all()


class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CouponSerializer
    queryset = Coupon.objects.all()
