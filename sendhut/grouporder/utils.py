from django.core.urlresolvers import resolve
from django.urls import reverse
from datetime import timedelta
from uuid import uuid4

from sendhut.cart.models import Cart
from sendhut.cart import CartStatus
from sendhut.cart.utils import get_or_create_anonymous_cart_from_token
from sendhut.lunch.models import Store

from .models import GroupOrder, Member
from . import MemberStatus


CART_PREFIX = 'group-order'


def set_group_order_cookie(group_order, response, token=None):
    """Update response with a group ordr token cookie."""
    ten_years = timedelta(days=(365 * 10))
    COOKIE_NAME = get_store_group_order_cookie_name(group_order.store)
    token = token or uuid4()
    response.set_signed_cookie(
        COOKIE_NAME, token, max_age=int(ten_years.total_seconds()))


def get_store_group_order_cookie_name(store):
    return '{}-{}'.format(CART_PREFIX, store.slug)


def join_group_order(user, group_order):
    member = Member.objects.filter(group_order=group_order, user=user).first()
    if not member:
        cart = Cart.objects.create()
        Member.objects.create(cart=cart, group_order=group_order, user=user)
        return member

    return member


def get_anonymous_group_order_token(request, store):
    cookie_name = get_store_group_order_cookie_name(store)
    return request.get_signed_cookie(cookie_name, default=None)


def get_anonymous_group_order_member(request, store):
    token = get_anonymous_group_order_token(request, store)
    return Member.objects.filter(
        cart__token=token,
        group_order__status=CartStatus.OPEN).first()


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
    store = None
    ref = request.GET.get('cart_ref')
    if ref:
        group_order = GroupOrder.objects.filter(token=ref).first()
        store = group_order.store if group_order else None
    else:
        try:
            match = resolve(request.path)
            if match.url_name == 'store_details':
                store = Store.objects.get(slug=match.kwargs['slug'])

            if match.url_name in ['leave', 'rejoin', 'cancel']:
                group_order = GroupOrder.objects.get(token=match.kwargs['ref'])
                store = group_order.store
        except:
            pass

    if store:
        if request.user.is_authenticated:
            # TODO(yao): filter for only groups users is active in NOW
            member = Member.objects.filter(
                group_order__store=store,
                group_order__status=CartStatus.OPEN,
                state=MemberStatus.IN,
                user=request.user).first()

            return member

        # anonymous users
        return get_anonymous_group_order_member(request, store)


def get_group_share_url(request, group_order):
    url = reverse('join-group-order', args=(group_order.token,))
    return request.build_absolute_uri(url)


def get_active_user_group_orders(user):
    return GroupOrder.objects.filter(
        status=CartStatus.OPEN, members__user=user)
