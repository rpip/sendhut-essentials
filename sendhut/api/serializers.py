from rest_framework import serializers


from sendhut.accounts.models import User, Address
from sendhut.lunch.models import (
    Vendor, Menu, Item, OptionGroup, Option,
    Image, OrderLine, Order, GroupCart, GroupCartMember
)


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


class VendorSerializer(serializers.ModelSerializer):

    menus = MenuSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return [x.name for x in obj.tags.all()]

    class Meta:
        model = Vendor
        fields = ('name', 'manager_name', 'address', 'phone',
                  'logo', 'email', 'slug', 'banner', 'tags',
                  'verified', 'available', 'menus', 'uuid')


class GroupCartMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupCartMember
        fields = ('name', 'cart', 'id')


class GroupCartSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    owner = UserSerializer(read_only=True)
    vendor = serializers.SerializerMethodField()

    def get_vendor(self, obj):
        return str(obj.vendor.uuid)

    def get_url(self, obj):
        return obj.get_absolute_url()

    class Meta:
        model = GroupCart
        fields = ('token', 'owner', 'vendor', 'monetary_limit', 'status', 'url')


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('image',)


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('name', 'price')


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
    group_cart = GroupCartSerializer(many=True, read_only=True)
    items = OrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('reference', 'delivery_time', 'delivery_address',
                  'delivery_fee', 'notes', 'total_cost', 'payment',
                  'payment_source', 'group_cart', 'items')
