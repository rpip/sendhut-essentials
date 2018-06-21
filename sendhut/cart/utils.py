from datetime import timedelta

from django.conf import settings
from djmoney.money import Money

from sendhut.utils import unquantize_for_paystack
from .models import Cart
from uuid import UUID

COOKIE_NAME = 'cart'


def set_cart_cookie(cart, response):
    """Update respons with a cart token cookie."""
    ten_years = timedelta(days=(365 * 10))
    response.set_signed_cookie(
        COOKIE_NAME, cart.token, max_age=int(ten_years.total_seconds()))


def token_is_valid(token):
    """Validate a cart token."""
    if token is None:
        return False
    if isinstance(token, UUID):
        return True
    try:
        UUID(token)
    except ValueError:
        return False
    return True


def get_or_create_anonymous_cart_from_token(
        token, cart_queryset=Cart.objects.all()):
    """Return an open unassigned cart with given token or create a new one."""
    return cart_queryset.open().filter(token=token, user=None).get_or_create(
        defaults={'user': None})[0]


def get_or_create_user_cart(user, cart_queryset=Cart.objects.all()):
    """Return an open cart for given user or create a new one."""
    return cart_queryset.open().get_or_create(
        user=user, group_member=None)[0]


def get_or_create_cart_from_request(request, cart_queryset=Cart.objects.all()):
    """Fetch cart from database or create a new one based on cookie."""
    if request.user.is_authenticated:
        return get_or_create_user_cart(request.user, cart_queryset)

    token = request.get_signed_cookie(COOKIE_NAME, default=None)
    return get_or_create_anonymous_cart_from_token(token, cart_queryset)


def get_cart_from_request(request, cart_queryset=Cart.objects.all()):
    """Fetch cart from database or return a new instance based on cookie."""
    if request.user.is_authenticated:
        cart = get_user_cart(request.user, cart_queryset)
        user = request.user
    else:
        token = request.get_signed_cookie(COOKIE_NAME, default=None)
        cart = get_anonymous_cart_from_token(token, cart_queryset)
        user = None

    if cart is not None:
        return cart

    return Cart(user=user)


def get_anonymous_cart_from_token(token, cart_queryset=Cart.objects.all()):
    """Return an open unassigned cart with given token if any."""
    return cart_queryset.open().filter(token=token, user=None).first()


def get_user_cart(user, cart_queryset=Cart.objects.all()):
    """Return an open cart for given user if any.
    Every logged in user has a cart which was transfered from anonymous
    cookie after user logged in.
    """
    return cart_queryset.open().filter(user=user).first()


def get_cart_data(cart, group_member=None, coupon=None):
    """Return a JSON-serializable representation of the cart."""
    delivery_fee = Money(settings.BASE_DELIVERY_FEE, settings.DEFAULT_CURRENCY)
    bowl_charge_total = cart.bowl_charge_total

    if group_member:
        cart = group_member.group_order
        total = cart.get_total()
    else:
        total = cart.get_total() + delivery_fee

    data = {
        'sub_total': cart.get_subtotal(),
        'delivery_fee': delivery_fee,
        'cart_delivery_fee': delivery_fee,
        'total': total,
        'unquantized_total': unquantize_for_paystack(total.amount),
        'bowl_charge_total': bowl_charge_total
    }
    # TODO(yao): filter out items not in giveaway stores
    return apply_discount(data, coupon) if coupon else data


def apply_discount(cart_data, coupon):
    balance_total = cart_data['total'] - coupon.giveaway.discount_value
    cart_data['pay_balance'] = pay_balance = balance_total.amount > 0
    cart_data['total'] = balance_total if pay_balance else 0
    return cart_data


def transfer_prelogin_cart(prelogin_cart, user):
    "Transfers items added before login to the user"
    cart = get_user_cart(user)
    cart.load_from_cart(prelogin_cart)
    prelogin_cart.hard_delete()
    return cart
