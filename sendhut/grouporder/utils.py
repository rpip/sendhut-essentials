from django.core.urlresolvers import resolve

from sendhut.cart.models import Cart
from sendhut.lunch.models import Store
from sendhut.cart.utils import get_or_create_anonymous_cart_from_token

from .models import GroupOrder, Member


CART_PREFIX = 'group-order'


def get_store_group_order_cookie_name(store):
    return '{}-{}'.format(CART_PREFIX, store.slug)


def join_group_order(user, group_order):
    member = Member.objects.filter(group_order=group_order, user=user).first()
    if not member:
        cart = Cart.objects.create(user=user)
        Member.objects.create(cart=cart, group_order=group_order, user=user)
        return member

    return member


def get_anonymous_group_order_token(request, store):
    cookie_name = get_store_group_order_cookie_name(store)
    return request.get_signed_cookie(cookie_name, default=None)


def get_anonymous_group_order_member(request, store):
    token = get_anonymous_group_order_token(request, store)
    return Member.objects.filter(cart__token=token).first()


def join_group_order_anonymous(request, group_order, name):
    member = get_anonymous_group_order_member(request, group_order.store)
    if not member:
        token = get_anonymous_group_order_token(request, group_order.store)
        cart = get_or_create_anonymous_cart_from_token(token)
        return Member.objects.create(group_order=group_order, cart=cart, name=name)

    return member


def create_group_order(user, store, monetary_limit=None):
    group_order = GroupOrder.objects.create(
        user=user, store=store, monetary_limit=monetary_limit)

    member = join_group_order(user, group_order)
    return group_order, member


def get_group_member_from_request(request):
    if request.GET.get('cart_ref'):
        return GroupOrder.objects.get(request.GET['cart_ref'])

    match = resolve(request.path)
    if match.url_name == 'store_details':
        store = Store.objects.get(slug=match.kwargs['slug'])

        if request.user.is_authenticated:
            user = request.user

            return Member.objects.filter(group_order__store=store, user=user).first()
        # anonymous users
        return get_anonymous_group_order_member(request, store)
