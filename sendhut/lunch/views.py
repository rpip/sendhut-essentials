import json
from functools import reduce
import operator

from django.views import View
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models import Q
from djmoney.money import Money

from sendhut.cart import Cart, GroupMemberCart
from sendhut import payments
from sendhut import utils
from sendhut.accounts.models import User

from .models import (
    Item, Store, Order, OrderLine, GroupCart, GroupCartMember, FOOD_TAGS
)
from .forms import CheckoutForm, PartnerSignupForm, GroupOrderForm
from .group_order import GroupOrder


def food_detail(request, slug):
    template = 'lunch/_item_detail.html'
    item = Item.objects.get(slug=slug)
    context = {
        'item': item,
        'page_title': item.name,
        'group_cart_token': request.GET.get('cart_ref')
    }
    return render(request, template, context)


def cartline_detail(request, line_id, slug):
    template = 'lunch/_item_detail.html'
    item = Item.objects.get(slug=slug)
    cart_ref = request.GET.get('cart_ref')
    context = {
        'item': item,
        'page_title': item.name,
        'group_cart_token': cart_ref
    }
    if cart_ref:
        cart = GroupMemberCart(request, cart_ref)
    else:
        cart = Cart(request)

    context['cart_line'] = cart.get_line(line_id).serialize()
    return render(request, template, context)


def cartline_delete(request, line_id):
    cart_ref = request.GET.get('cart_ref')
    if cart_ref:
        GroupMemberCart(request, cart_ref).remove(line_id)
    else:
        Cart(request).remove(line_id)

    return JsonResponse({'status': 'OK'}, encoder=utils.JSONEncoder)


class PartnerSignupView(FormView):
    template_name = 'partner_signup.html'
    form_class = PartnerSignupForm
    page_title = 'Deliver with Sendhut'
    success_url = '/business/'

    def form_valid(self, form):
        info = """
        We will get back to you quickly, and we'll collect any more
        info we need to get you listed.
        """
        messages.info(self.request, info)
        Store.objects.create(**form.cleaned_data)
        # TODO(yao): send email and sms notification to merchant
        return super().form_valid(form)


def search(request, tag):
    subtags = FOOD_TAGS.tags_for(tag)
    results = Store.featured.filter(
        reduce(operator.or_, (Q(tags__name__icontains=q) for q in subtags)))
    context = {
        'page_title': 'search',
        'search_term': utils.unslugify(tag),
        'restaurants': results.distinct()
    }
    return render(request, 'lunch/search.html', context)


@login_required
def order_list(request):
    open_carts = GroupCart.get_user_open_carts(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(
        request,
        'lunch/order_history.html',
        {'orders': orders, 'open_carts': open_carts}
    )


@login_required
def order_details(request, ref):
    context = {
        'order': get_object_or_404(Order, user=request.user, reference=ref)
    }
    return render(request, 'lunch/order_details.html', context)


class GroupOrderView(LoginRequiredMixin, View):

    template_name = 'lunch/group_order.html'

    def post(self, request, *args, **kwargs):
        form = GroupOrderForm(data=request.POST)
        if form.is_valid():
            store = form.cleaned_data['store']
            limit = form.cleaned_data['limit']
            GroupOrder.create(request, store, limit)
            messages.info(request, "Group order created!")
            return redirect(reverse('lunch:store_details', args=(store,)))

        return redirect(request.META.get('HTTP_REFERER'))


def store_page(request, slug):
    template = 'lunch/store_details.html'
    store = get_object_or_404(Store, slug=slug)
    context = {
        'store': store,
        'page_title': store.name
    }
    group_order = GroupOrder.get_by_store(request, store.uuid)
    if group_order:
        # TODO(yao): update all sessions when group_order (groupcart)
        # is locked (cancelled,checkout), remove from
        # TODO(yao): mixin/plug/middleware to inject group_order context for every/req
        # if group_order is cancelled or locked, return to prev with error as
        # cancelled or 500 page with custom error message
        group_cart = GroupCart.objects.filter(token=group_order['token']).first()
        if group_cart and group_cart.is_open():
            member = group_cart.members.get(id=group_order['member']['id'])
            context['group_order'] = group_order
            context['cart'] = member.cart
            context['group_cart'] = group_cart
            context['cart_url'] = request.build_absolute_uri(
                group_cart.get_absolute_url())
        else:
            # cancelled or locked for checkout
            name = User.objects.get(email=group_order['owner']['email']).get_full_name()
            limit = Money(group_order['monetary_limit'], 'NGN')
            limit = ("({} limit)".format(limit) if limit else "")
            error_msg = "{}'s {} group order has expired".format(name, limit)
            messages.error(request, error_msg)
    else:
        messages.info(request, "You can order in lunch with coworkers or \
        friends with the group order.")

    return render(request, template, context)


class CartJoin(View):

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        group_cart = get_object_or_404(GroupCart, token=token)
        if request.user.is_authenticated():
            GroupOrder.join(request, group_cart, request.user.get_full_name())
            msg = "You've joined {}'s group order".format(group_cart.owner.get_full_name())
            messages.info(request, msg)
            return redirect(reverse('lunch:store_details', args=(group_cart.store.slug,)))

        # already in group cart
        if GroupOrder.get(request, token):
            return redirect(reverse('lunch:store_details',
                                    args=(group_cart.store.slug,)))

        context = {
            'group_cart': group_cart,
            'store': group_cart.store,
            'cart_url': request.build_absolute_uri(group_cart.get_absolute_url())
        }

        return render(request, 'lunch/cart_join.html', context)

    def post(self, request, *args, **kwargs):
        token = kwargs['token']
        group_cart = get_object_or_404(GroupCart, token=token)
        name = request.POST['name']
        if not name:
            return redirect(request.META.get('HTTP_REFERER'))

        GroupOrder.join(request, group_cart, name)
        msg = "You've joined {}'s group order".format(group_cart.owner.get_full_name())
        messages.info(request, msg)
        return redirect(reverse('lunch:store_details', args=(group_cart.store.slug,)))


class CartView(View):
    # TODO(yao): implement dynamic delivery cost calculation

    def get(self, request):
        token = request.GET.get('cart_ref')
        if token:
            cart = GroupMemberCart(request, token)
            context = cart.build_cart()
            context['group_cart'] = cart.member.group_cart
        else:
            context = Cart(request).build_cart()

        return render(request, 'partials/sidebar_cart.html', context)

    def post(self, request):
        "This endpoints handle new cart additions and cart item updates"
        data = json.loads(request.body)
        token = data.get('cart_token')
        if token:
            cart = GroupMemberCart(request, token)
        else:
            cart = Cart(request)

        item = Item.objects.get(uuid=data['uuid'])
        quantity = data.pop('quantity')
        # if line_id is present, it means it's an update
        cart.add(item, int(quantity), data, replace=data.get('line_id'))
        return JsonResponse(cart.build_cart(), encoder=utils.JSONEncoder)


@login_required
def cart_summary(request):
    ref = request.GET.get('cart_ref')
    if ref:
        cart = GroupMemberCart(request, ref)
        context = cart.build_cart()
        context['group_cart'] = cart.member.group_cart
    else:
        context = Cart(request).build_cart()

    context['form'] = CheckoutForm(data=request.POST)
    return render(request, 'lunch/cart_summary.html', context)


def cart_reload(request):
    template = 'lunch/cart_summary.html'
    ref = request.GET.get('cart_ref')
    if ref and ref != 'undefined':
        cart = GroupMemberCart(request, ref)
        context = cart.build_cart()
        context['group_cart'] = cart.member.group_cart
    else:
        context = Cart(request).build_cart()

    return render(request, template, context)


class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        form = CheckoutForm(data=request.POST)
        ref = request.GET.get('cart_ref')
        if ref:
            context = GroupOrder.build_cart(request, ref)
        else:
            context = Cart(request).build_cart()

        context['form'] = form
        return render(request, 'lunch/cart_summary.html', context)

    def post(self, request):
        form = CheckoutForm(data=request.POST)
        group_session = GroupOrder.get(request)
        if not(form.is_valid()):
            messages.error(request, "Please complete the delivery form to proceed")
            if group_session:
                ref = request.GET['cart_ref']
                context = GroupOrder.build_cart(request, ref)
            else:
                context = Cart(request).build_cart()

            return render(request, 'lunch/cart_summary.html', context)

        cart = Cart(request)
        cash_delivery = form.cleaned_data.pop('cash_delivery')
        # TODO(yao): send invoice email, send sms confirmation/updates
        _cart = cart.build_cart()
        group_cart = None
        cart_ref = request.GET.get('cart_ref')
        if cart_ref:
            group_cart = GroupCart.objects.get(token=cart_ref)
            group_cart.lock()

        order = Order.create_from_cart(
            cart=cart,
            user=request.user,
            group_cart=group_cart,
            total_cost=_cart['total'],
            delivery_fee=_cart['delivery_fee'],
            **form.cleaned_data
        )

        messages.info(
            request,
            "Order submitted for processing. reference {}".format(order.reference))

        if not(cash_delivery):
            amount = _cart['total']
            response = payments.initialize_payment(
                order.reference, amount, request.user.email)
            if response['status']:
                return redirect(response['data']['authorization_url'])
            else:
                # TODO(yao): what to do if payment fails
                messages.error(request, "Payment failed. Please try again")

        if group_cart:
            GroupOrder.end_session(request, cart_ref)

        return redirect('home')


def leave_group_order(request, token):
    group_cart = get_object_or_404(GroupCart, token=token)
    GroupOrder.leave(request, token)
    msg = "You've been removed from {}'s cart".format(
        group_cart.owner.get_full_name())
    messages.info(request, msg)
    return redirect(reverse('lunch:store_details',
                            args=(group_cart.store.slug,)))


def cancel_group_order(request, token):
    store_slug = GroupOrder.cancel(request, token)
    messages.info(request, "Group order deleted")
    return redirect(reverse('lunch:store_details', args=(store_slug,)))
