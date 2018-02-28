from django.conf import settings

from djmoney.money import Money

from .models import GroupCart, GroupCartMember, Vendor
from sendhut.api.serializers import GroupCartSerializer, GroupCartMemberSerializer


class GroupOrder:

    @classmethod
    def create(cls, request, vendor_slug, limit=None):
        vendor = Vendor.objects.get(slug=vendor_slug)
        group_cart = GroupCart.objects.create(
            owner=request.user,
            vendor=vendor,
            monetary_limit=limit
        )
        member = GroupCartMember.objects.create(
            user=request.user,
            group_cart=group_cart,
            name=request.user.get_full_name()
        )
        group_cart.members.add(member)
        data = cls.serialize(group_cart)
        return cls.add_to_session(request, data, member)

    @classmethod
    def serialize(cls, group_cart):
        return GroupCartSerializer(instance=group_cart).data

    @classmethod
    def join(cls, request, group_cart, name=None):
        if request.user.is_authenticated():
            GroupCartMember.objects.create(
                user=request.user,
                group_cart=group_cart,
                name=request.user.get_full_name())

        member = GroupCartMember.objects.create(group_cart=group_cart, name=name)
        return cls.add_to_session(request, cls.serialize(group_cart), member)

    @classmethod
    def add_to_session(cls, request, group_order, member):
        token = group_order['token']
        if not cls.get(request, token):
            # if first group order
            if not cls.get(request):
                request.session[settings.GROUP_CART_SESSION_ID] = {}

            group_order['member'] = GroupCartMemberSerializer(instance=member).data
            request.session[settings.GROUP_CART_SESSION_ID][token] = group_order
            request.session.modified = True

        return group_order['url']

    @classmethod
    def get(cls, request, cart_token=None):
        group_orders = request.session.get(settings.GROUP_CART_SESSION_ID, {})
        if group_orders and cart_token:
            return group_orders.get(cart_token, {})

        return group_orders

    @classmethod
    def build_cart(cls, request, cart_token):
        group_order = cls.get(request, cart_token)
        cart = {}
        if group_order:
            token = group_order['token']
            group_cart = GroupCart.objects.get(token=token)
            sub_total = sum([Money(x.cart['sub_total'], 'NGN') for x
                             in group_cart.members.all() if x.cart])
            delivery_fee = Money(settings.LUNCH_DELIVERY_FEE, 'NGN')
            cart['group_cart_session'] = token
            cart['group_cart'] = group_cart
            cart['delivery_fee'] = delivery_fee
            cart['sub_total'] = sub_total
            cart['total'] = sub_total + delivery_fee

        return cart

    @classmethod
    def end_session(cls, request, token):
        del request.session[settings.GROUP_CART_SESSION_ID][token]
        request.session.modified = True

    @classmethod
    def update_member_cart(cls, group_order, cart):
        member = GroupCartMember.objects.get(id=group_order['member']['id'])
        member.cart = cart
        member.save()

    @classmethod
    def get_by_vendor(cls, request, vendor_uuid):
        return next((v for k, v in cls.get(request).items() if v['vendor'] == str(vendor_uuid)), {})

    @classmethod
    def cancel(cls, request, token):
        group_cart = GroupCart.objects.get(token=token)
        slug = group_cart.vendor.slug
        group_cart.delete()
        GroupOrder.end_session(request, token)
        return slug

    @classmethod
    def leave(cls, request, token):
        group_order = cls.get(request, token)
        member = GroupCartMember.objects.get(
            group_cart__token=token,
            id=group_order['member']['id']
        )
        member.leave_cart()
        cls.end_session(request, token)
