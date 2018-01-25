import json
from datetime import datetime

from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.cache import cache_page
from django.urls import reverse
from djmoney.money import Money

from .models import (
    Item, Vendor, Order, OrderLine, GroupCart, GroupCartMember, FOOD_TAGS
)
from .forms import CheckoutForm
from sendhut.cart import Cart
from sendhut import payments
from sendhut import utils

# TODO(yao): reorganize around domains: vendor, cart, food

from functools import reduce
import operator
from django.db.models import Q


@cache_page(60 * 60)
def search(request, tag):
    # TODO(yao): Move search into component
    # TODO(yao): search food and menus tags
    subtags = FOOD_TAGS.tags_for(tag)
    results = Vendor.objects.filter(
        reduce(operator.or_, (Q(tags__name__icontains=q) for q in subtags)))
    context = {
        'page_title': 'search',
        'search_term': utils.unslugify(tag),
        'restaurants': results
    }
    return render(request, 'lunch/search.html', context)


@cache_page(60 * 60)
def vendor_page(request, slug):
    template = 'lunch/vendor_details.html'
    vendor = get_object_or_404(Vendor, slug=slug)
    context = {
        'vendor': vendor,
        'page_title': vendor.name,
    }
    if GroupOrder.get(request):
        data = GroupOrder.get(request)
        context.update(data)
        context['group_cart'] = GroupCart.objects.get(name=data['reference'])
    else:
        messages.info(request, "You can order in lunch with coworkers or \
        friends with the group order.")

    return render(request, template, context)


@cache_page(60 * 60)
def food_detail(request, slug):
    template = 'lunch/_item_detail.html'
    item = Item.objects.get(slug=slug)
    context = {
        'item': item,
        'page_title': item.name
    }
    return render(request, template, context)


@cache_page(60 * 60)
def cartline_detail(request, line_id, slug):
    template = 'lunch/_item_detail.html'
    item = Item.objects.get(slug=slug)
    cart = Cart(request)
    context = {
        'item': item,
        'page_title': item.name,
        'cart_line': cart.get_line(line_id).serialize()
    }
    return render(request, template, context)


def cartline_delete(request, line_id):
    Cart(request).remove(line_id)
    return JsonResponse({'status': 'OK'}, encoder=utils.JSONEncoder)


class CartView(View):
    # TODO(yao): implement dynamic delivery cost calculation

    def get(self, request):
        # /cart
        if request.GET.get('clear'):
            Cart(request).clear()

        context = Cart(request).build_cart()
        context.update(GroupOrder.build_cart(request))
        return render(request, 'partials/sidebar_cart.html', context)

    def post(self, request):
        "This endpoints handle new cart additions and cart item updates"
        cart = Cart(request)
        data = json.loads(request.body)
        # if line_id is present, it means it's an update
        # delete cart line and re-add
        if data and data.get('line_id'):
            cart.remove(data.get('line_id'))

        item = Item.objects.get(uuid=data['uuid'])
        quantity = data.pop('quantity')
        cart.add(item, int(quantity), data)
        return JsonResponse(cart.build_cart(), encoder=utils.JSONEncoder)


@login_required
def cart_summary(request):
    context = Cart(request).build_cart()
    context.update(GroupOrder.build_cart(request))
    context['form'] = CheckoutForm(data=request.POST)
    return render(request, 'lunch/cart_summary.html', context)


def cart_reload(request):
    group_session = GroupOrder.get(request)
    template = 'lunch/_cart_summary.html'
    if group_session:
        template = 'lunch/_group_cart_summary.html'
        context = GroupOrder.build_cart(request)
    else:
        context = Cart(request).build_cart()

    return render(request, template, context)


@login_required
@cache_page(60 * 60)
def order_list(request):
    context = {
        'orders': Order.objects.filter(user=request.user)
    }
    return render(request, 'lunch/order_list.html', context)


@login_required
@cache_page(60 * 60)
def order_details(request, reference):
    context = {
        'order': get_object_or_404(Order, user=request.user, reference=reference)
    }
    return render(request, 'lunch/order_details.html', context)


class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        form = CheckoutForm(data=request.POST)
        group_session = GroupOrder.get(request)
        if group_session:
            context = GroupOrder.build_cart(request)
        else:
            context = Cart(request).build_cart()

        context['form'] = form
        return render(request, 'lunch/cart_summary.html', context)

    def post(self, request):
        form = CheckoutForm(data=request.POST)
        if not(form.is_valid()):
            messages.error(request, "Please complete the delivery form to proceed")
            group_session = GroupOrder.get(request)
            if group_session:
                context = GroupOrder.build_cart(request)
            else:
                context = Cart(request).build_cart()

            return render(request, 'lunch/cart_summary.html', context)

        delivery_time = form.cleaned_data['delivery_time']
        hour, minute = delivery_time.split(':')
        delivery_time = datetime.today().replace(hour=int(hour), minute=int(minute))
        delivery_address = form.cleaned_data['delivery_address']
        notes = form.cleaned_data['notes']
        cash_delivery = form.cleaned_data['cash_delivery']
        cart = Cart(request)
        # TODO(yao): send invoice email, send sms confirmation/updates
        _cart = cart.build_cart()
        order = Order.objects.create(
            user=request.user,
            delivery_time=delivery_time,
            notes=notes,
            total_cost=_cart['total'],
            delivery_address=delivery_address,
            delivery_fee=_cart['delivery_fee']
        )
        for line in cart:
            data = line.serialize()
            OrderLine.objects.create(
                item_id=line.id,
                quantity=line.get_quantity(),
                price=line.get_total(),
                order=order,
                special_instructions=data['note'],
                metadata=utils.json_encode(data)
            )
        # cart.clear()
        messages.info(request, "Order submitted for processing. reference {}".format(order.reference))
        if not(cash_delivery):
            amount = _cart['total'].amount
            response = payments.initialize_payment(order, amount, request.user.email)
            if response['status']:
                return redirect(response['data']['authorization_url'])
            else:
                # TODO(yao): what to do if payment fails
                messages.error(request, "Payment failed")

        return redirect('home')


class GroupOrderView(LoginRequiredMixin, View):

    template_name = 'lunch/group_order.html'

    def post(self, request, *args, **kwargs):
        limit = request.POST['limit']
        # own limit
        other_limit = request.POST['other_limit']
        limit = float(limit) if limit else None
        limit = float(other_limit) if other_limit else limit
        vendor_slug = request.POST['vendor'].strip()
        vendor = Vendor.objects.get(slug=vendor_slug)
        GroupOrder.new(request, vendor, limit)
        messages.info(request, "Group order created!")
        return redirect(reverse('lunch:vendor_details', args=(vendor.slug,)))


class CartJoin(View):

    def get(self, request, *args, **kwargs):
        reference = kwargs['reference']
        group_cart = get_object_or_404(GroupCart, name=reference)
        GroupOrder.start_session(request, group_cart)
        return redirect(reverse('lunch:vendor_details', args=(group_cart.vendor.slug,)))

    def post(self, request, *args, **kwargs):
        reference = kwargs['reference']
        group_cart = get_object_or_404(GroupCart, name=reference)
        name = request.POST['name']
        if not name:
            return redirect(request.META.get('HTTP_REFERER'))

        found = group_cart.members.filter(name=name)
        if not found:
            member = GroupCartMember.objects.create(
                group_cart=group_cart,
                name=name
            )
            GroupOrder.join_cart(request, member)
            msg = "You've joined {}'s group order".format(group_cart.owner.get_full_name())
            messages.info(request, msg)

        return redirect(reverse('lunch:vendor_details', args=(group_cart.vendor.slug,)))


def leave_group_order(request, reference):
    group_cart = get_object_or_404(GroupCart, name=reference)
    member = GroupOrder.get_cart_member(request)
    group_cart.members.filter(id=member['id']).delete()
    msg = "You've been removed from {}'s cart".format(group_cart.owner.get_full_name())
    messages.info(request, msg)
    GroupOrder.end_session(request)
    return redirect(reverse('lunch:vendor_details', args=(group_cart.vendor.slug,)))


def cancel_group_order(request, reference):
    group_cart = get_object_or_404(GroupCart, name=reference)
    group_cart.delete()
    vendor_slug = group_cart.vendor.slug
    GroupOrder.end_session(request)
    # TODO(yao): push/notify to all participating clients when group order is cancelled
    messages.info(request, "Group order deleted")
    return redirect(reverse('lunch:vendor_details', args=(vendor_slug,)))


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
            group_cart = get_object_or_404(GroupCart, name=reference)
            sub_total = sum([Money(x.cart['sub_total'], 'NGN') for x in group_cart.members.all() if x.cart])
            delivery_fee = Money(settings.LUNCH_DELIVERY_FEE, 'NGN')
            cart['group_cart_session'] = group_cart_session
            cart['group_cart'] = group_cart
            cart['delivery_fee'] = delivery_fee
            cart['sub_total'] = sub_total
            cart['total'] = sub_total + delivery_fee

        return cart

    @classmethod
    def end_session(cls, request):
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
