from django.conf import settings
from django.urls import reverse

from djmoney.money import Money

from .models import GroupCart, GroupCartMember


class GroupOrder:

    @classmethod
    def new(cls, request, vendor, limit=None):
        # TODO(yao): maybe confirm clear existing Cart before proceeding?
        group_cart = GroupCart.objects.create(
            owner=request.user,
            vendor=vendor,
            monetary_limit=limit)
        member = GroupCartMember.objects.create(
            user=request.user,
            group_cart=group_cart,
            name=request.user.get_full_name()
        )
        group_cart.members.add(member)
        return cls.start_session(request, group_cart, member)

    @classmethod
    def start_session(cls, request, group_cart, member=None):
        url = reverse('lunch:cart_join', args=(group_cart.name, ))
        group_cart_url = request.build_absolute_uri(url)
        member = {'name': member.name, 'id': member.id} if member else None
        if not cls.get(request):
            request.session[settings.GROUP_CART_SESSION_ID] = {
                'url': group_cart_url,
                'reference': group_cart.name,
                'uuid': str(group_cart.uuid),
                'force_signup': not(request.user.is_authenticated()),
                'member': member
            }
            request.session.modified = True
        return group_cart_url

    @classmethod
    def get(cls, request):
        return request.session.get(settings.GROUP_CART_SESSION_ID, {})

    @classmethod
    def build_cart(cls, request):
        group_cart_session = GroupOrder.get(request)
        cart = {}
        if group_cart_session:
            reference = group_cart_session['reference']
            group_cart = GroupCart.objects.get(name=reference)
            sub_total = sum([Money(x.cart['sub_total'], 'NGN') for x
                             in group_cart.members.all() if x.cart])
            delivery_fee = Money(settings.LUNCH_DELIVERY_FEE, 'NGN')
            cart['group_cart_session'] = group_cart_session
            cart['group_cart'] = group_cart
            cart['delivery_fee'] = delivery_fee
            cart['sub_total'] = sub_total
            cart['total'] = sub_total + delivery_fee

        return cart

    @classmethod
    def end_session(cls, request):
        if cls.get(request):
            del request.session[settings.GROUP_CART_SESSION_ID]
            request.session.modified = True

    @classmethod
    def force_signup(cls, request):
        request.session[settings.GROUP_CART_SESSION_ID]['force_signup'] = True
        request.session.modified = True

    @classmethod
    def join_cart(cls, request, member):
        member = {'name': member.name, 'id': member.id}
        request.session[settings.GROUP_CART_SESSION_ID]['member'] = member
        request.session[settings.GROUP_CART_SESSION_ID]['force_signup'] = False
        request.session.modified = True

    @classmethod
    def get_cart_member(cls, request):
        return request.session[settings.GROUP_CART_SESSION_ID]['member']

    @classmethod
    def update_member_cart(cls, group_cart, cart, member):
        group_cart = GroupCart.objects.get(name=group_cart['reference'])
        member = group_cart.members.filter(id=member['id'])[0]
        member.cart = cart
        member.save()
