import json
from datetime import datetime
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

from sendhut.cart import Cart, GroupMemberCart
from sendhut import payments
from sendhut import utils

from .models import (
    Item, Vendor, Order, OrderLine, GroupCart, GroupCartMember, FOOD_TAGS
)
from .forms import CheckoutForm, VendorSignupForm, GroupOrderForm
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
        cart_line = GroupOrder.get_line(request, cart_ref)
    else:
        cart = Cart(request)
        cart_line = cart.get_line(line_id).serialize()

    context['cart_line'] = cart_line
    return render(request, template, context)


def cartline_delete(request, line_id):
    Cart(request).remove(line_id)
    return JsonResponse({'status': 'OK'}, encoder=utils.JSONEncoder)


class VendorSignupView(FormView):
    template_name = 'vendor_signup.html'
    form_class = VendorSignupForm
    page_title = 'Deliver with Sendhut'
    success_url = '/business/'

    def form_valid(self, form):
        info = """
        We will get back to you quickly, and we'll collect any more
        info we need to get you listed.
        """
        messages.info(self.request, info)
        Vendor.objects.create(**form.cleaned_data)
        # TODO(yao): send email and sms notification to merchant
        return super().form_valid(form)


def search(request, tag):
    subtags = FOOD_TAGS.tags_for(tag)
    results = Vendor.objects.filter(
        reduce(operator.or_, (Q(tags__name__icontains=q) for q in subtags)))
    context = {
        'page_title': 'search',
        'search_term': utils.unslugify(tag),
        'restaurants': results
    }
    return render(request, 'lunch/search.html', context)


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'lunch/order_history.html', {'orders': orders})


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
            vendor = form.cleaned_data['vendor']
            limit = form.cleaned_data['limit']
            GroupOrder.create(request, vendor, limit)
            messages.info(request, "Group order created!")
            return redirect(reverse('lunch:vendor_details', args=(vendor,)))

        return redirect(request.META.get('HTTP_REFERER'))


def vendor_page(request, slug):
    template = 'lunch/vendor_details.html'
    vendor = get_object_or_404(Vendor, slug=slug)
    context = {
        'vendor': vendor,
        'page_title': vendor.name
    }
    group_order = GroupOrder.get_by_vendor(request, vendor.uuid)
    if group_order:
        group_cart = GroupCart.objects.get(token=group_order['token'])
        member = group_cart.members.get(id=group_order['member']['id'])
        context['group_order'] = group_order
        context['cart'] = member.cart
        context['group_cart'] = group_cart
        context['cart_url'] = request.build_absolute_uri(
            group_cart.get_absolute_url())
    else:
        messages.info(request, "You can order in lunch with coworkers or \
        friends with the group order.")

    return render(request, template, context)


class CartJoin(View):

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        group_cart = get_object_or_404(GroupCart, token=token)

        # already in group cart
        if GroupOrder.get(request, token):
            return redirect(reverse('lunch:vendor_details',
                                    args=(group_cart.vendor.slug,)))

        context = {
            'group_cart': group_cart,
            'vendor': group_cart.vendor,
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
        return redirect(reverse('lunch:vendor_details', args=(group_cart.vendor.slug,)))


class CartView(View):
    # TODO(yao): implement dynamic delivery cost calculation

    def get(self, request):
        token = request.GET.get('cart_ref')
        if token:
            cart = GroupMemberCart(request, token)
            context = cart.build_cart()
            group_order = GroupOrder.get(request, token)
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
    ref = request.GET['cart_ref']
    context = Cart(request).build_cart()
    context.update(GroupOrder.build_cart(request, ref))
    context['form'] = CheckoutForm(data=request.POST)
    return render(request, 'lunch/cart_summary.html', context)


def cart_reload(request):
    group_session = GroupOrder.get(request)
    template = 'lunch/_cart_summary.html'
    if group_session:
        ref = request.GET['cart_ref']
        template = 'lunch/_group_cart_summary.html'
        context = GroupOrder.build_cart(request, ref)
    else:
        context = Cart(request).build_cart()

    return render(request, template, context)


class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        form = CheckoutForm(data=request.POST)
        group_session = GroupOrder.get(request)
        if group_session:
            ref = request.GET['cart_ref']
            context = GroupOrder.build_cart(request, ref)
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
                ref = request.GET['cart_ref']
                context = GroupOrder.build_cart(request, ref)
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
        ref = request.GET['cart_ref']
        group_session = GroupOrder.get(request, ref)
        order = Order.objects.create(
            user=request.user,
            group_cart=group_cart,
            delivery_time=delivery_time,
            notes=notes,
            total_cost=_cart['total'],
            delivery_address=delivery_address,
            delivery_fee=_cart['delivery_fee']
            #metadata={'session':  {x.id: x.cart for x in group_cart.members.all()}}
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
        messages.info(request, "Order submitted for processing. reference {}".format(order.reference))
        if not(cash_delivery):
            amount = _cart['total']
            response = payments.initialize_payment(order.reference, amount, request.user.email)
            if response['status']:
                return redirect(response['data']['authorization_url'])
            else:
                # TODO(yao): what to do if payment fails
                messages.error(request, "Payment failed")

        return redirect('home')


def leave_group_order(request, token):
    group_cart = get_object_or_404(GroupCart, token=token)
    GroupOrder.leave(request, token)
    msg = "You've been removed from {}'s cart".format(
        group_cart.owner.get_full_name())
    messages.info(request, msg)
    return redirect(reverse('lunch:vendor_details',
                            args=(group_cart.vendor.slug,)))


def cancel_group_order(request, token):
    vendor_slug = GroupOrder.cancel(request, token)
    messages.info(request, "Group order deleted")
    return redirect(reverse('lunch:vendor_details', args=(vendor_slug,)))
