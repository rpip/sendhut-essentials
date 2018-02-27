from rest_framework import viewsets

from sendhut.accounts.models import User, Address
from sendhut.lunch.models import (
    Vendor, Item, Order, GroupCart
)

from . import serializers


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AddressSerializer
    queryset = Address.objects.all()


class VendorViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.VendorSerializer
    queryset = Vendor.objects.all()


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ItemSerializer
    queryset = Item.objects.all()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all()


class GroupCartViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GroupCartSerializer
    queryset = GroupCart.objects.all()
