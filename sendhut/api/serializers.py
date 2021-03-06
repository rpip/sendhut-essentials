from rest_framework import serializers


from sendhut.accounts.models import User, Address
from sendhut.stores.models import (
    Store, Menu, Item, OptionGroup, Option, Image
)
from sendhut.checkout.models import Order, OrderLine


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('city', 'county', 'location')


class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'addresses',
                  'username', 'phone', 'last_login', 'identity_verified')


class MenuSerializer(serializers.ModelSerializer):

    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return [x.name for x in obj.tags.all()]

    class Meta:
        model = Menu
        fields = ('name', 'tags', 'info', 'items')
        depth = 1


class StoreSerializer(serializers.ModelSerializer):

    menus = MenuSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return [x.name for x in obj.tags.all()]

    class Meta:
        model = Store
        fields = ('name', 'manager_name', 'address', 'phone',
                  'logo', 'email', 'slug', 'banner', 'tags',
                  'verified', 'available', 'menus', 'uuid')


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('image',)


class OptionSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    def get_parent(self, obj):
        return obj.group.name

    class Meta:
        model = Option
        fields = ('id', 'uuid', 'name', 'price', 'parent')


class OptionGroupSerializer(serializers.ModelSerializer):
    values = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = OptionGroup
        fields = ('name', 'is_required', 'multi_select', 'values')


class ItemSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    options = OptionGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ('name', 'slug', 'description', 'price',
                  'dietary_labels', 'images', 'available',
                  'available', 'options')


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ('item', 'quantity', 'price', 'special_instructions')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('reference', 'delivery_time', 'delivery_address',
                  'delivery_fee', 'notes', 'total_cost', 'payment',
                  'payment_source', 'group_cart', 'items')
