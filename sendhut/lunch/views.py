import json
from datetime import datetime

from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from djmoney.money import Money

from .models import Item, Vendor, Order, OrderLine, GroupCart, GroupCartMember
from .forms import CheckoutForm, GroupOrderForm
from sendhut.cart import Cart
from sendhut import payments
from sendhut import utils

# TODO(yao): reorganize around domains: vendor, cart, food


def search(request, tag):
    # TODO(yao): Move search into component
    # TODO(yao): search food and menus tags
    context = {
        'page_title': 'search',
        'search_term': utils.unslugify(tag),
        'restaurants': Vendor.objects.filter(tags__name__in=[tag])
    }
    return render(request, 'lunch/search.html', context)


def vendor_page(request, slug):
    if GroupOrder.in_session(request):
        messages.info(request, "You are in a group order now. Your cart will be added to the group order")
    else:
        messages.info(request, "You can order in lunch with coworkers or \
        friends with the group order.")

    template = 'lunch/vendor_details.html'
    vendor = get_object_or_404(Vendor, slug=slug)
    context = {
        'vendor': vendor
    }
    return render(request, template, context)


def food_detail(request, slug):
    template = 'lunch/_item_detail.html'
    item = Item.objects.get(slug=slug)
    context = {
        'item': item,
        'page_title': item.name
    }
    return render(request, template, context)


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
        if GroupOrder.in_session(request):
            group_cart = GroupOrder.get(request)
            context['group_cart'] =  GroupCart.objects.get(uuid=group_cart['uuid'])

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


def cart_summary(request):
    # if GroupOrder.in_session(request):
    context = Cart(request).build_cart()
    context['form'] = CheckoutForm(data=request.POST)
    return render(request, 'lunch/cart_summary.html', context)


def cart_reload(request):
    cart = Cart(request).build_cart()
    return render(request, 'lunch/_cart_summary.html', cart)


@login_required
def order_list(request):
    context = {
        'orders': Order.objects.filter(user=request.user)
    }
    return render(request, 'lunch/order_list.html', context)


@login_required
def order_details(request, reference):
    context = {
        'order': get_object_or_404(Order, user=request.user, reference=reference)
    }
    return render(request, 'lunch/order_details.html', context)


class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        form = CheckoutForm(data=request.POST)
        if GroupOrder.in_session(request):
            context = GroupOrder.get(request)
        else:
            context = Cart(request).build_cart()

        context['form'] = form
        return render(request, 'lunch/cart_summary.html', context)

    def post(self, request):
        form = CheckoutForm(data=request.POST)
        if not(form.is_valid()):
            messages.error(request, "Please complete the delivery form to proceed")
            context = Cart(request).build_cart()
            context['form'] = form
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

    def get(self, request, *args, **kwargs):
        vendor_slug = kwargs['slug']
        context = {
            'form': GroupOrderForm(),
            'vendor': Vendor.objects.get(slug=vendor_slug)
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = GroupOrderForm(request.POST)
        vendor = Vendor.objects.get(slug=kwargs['slug'])
        if form.is_valid():
            limit = form.cleaned_data['monetary_limit']
            group_cart_url = GroupOrder.new(request, vendor, limit)
            context = {
                'group_cart_url': group_cart_url,
                'vendor': vendor
            }
            messages.info(request, "Group order created!")
            return render(request, self.template_name, context)
        else:
            context = {'form': form, 'vendor': vendor}
            return render(request, self.template_name, context)


def join_group_order(request, name):
    group_cart = get_object_or_404(GroupCart, name)
    if request.user.is_authenticated():
        found = group_cart.members.filter(email=request.user.email)
        if found:
            msg = "You're already part of the {} group order".format(
                group_cart.name)
            messages.info(request, msg)
        else:
            GroupCartMember.objects.create(
                user=request.user,
                group_cart=group_cart,
                email=request.user.email,
                phone=request.user.phone
            )
            messages.info(request, "You've joined {} group order".format(group_cart.name))
    else:
        pass


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
            email=request.user.email,
            phone=request.user.phone
        )
        group_cart.members.add(member)
        from django.urls import reverse
        url = reverse('group_order_join', args=(group_cart.name, ))
        group_cart_url = request.build_absolute_uri(url)
        request.session[settings.GROUP_CART_SESSION_ID] = {
            'url': group_cart_url,
            'uuid': str(group_cart.uuid)
        }
        request.session.modified = True
        return group_cart_url

    @classmethod
    def in_session(cls, request):
        return request.session.get(settings.GROUP_CART_SESSION_ID)

    @classmethod
    def get(cls, request):
        return request.session.get(settings.GROUP_CART_SESSION_ID, {})


def group_order_submit(request):
    # TODO(yao): unauthenticated user
    parent_cart = GroupOrder.get(request)
    group_cart = GroupCart.objects.get(uuid=parent_cart['uuid'])
    # clear cart, exit group order session, redirect to cart summary
    user = request.user
    cart = Cart(request)
    if user.is_authenticated():
        member = GroupCartMember.objects.get(user=user, group_cart=group_cart)
        # TODO(yao): Remove Money objects from cart.py
        member.cart = json.loads(utils.json_encode(cart.build_cart(is_group_order=True)))
        # TODO(yao): alert owner of group order
        member.save()
        messages.info(request, "Your cart has been added to the group order")
    # if not logged in, grab info from session: email, phone
    # create group_cart_member object, attach cart, add member to group cart
    # proceed

    total = sum([Money(x.cart['sub_total']) for x in group_cart.members.all()])
    context = {
        'group_cart': group_cart,
        'sub_total': total,
        'delivery_fee': Money(settings.LUNCH_DELIVERY_FEE, 'NGN')
    }
    return render(request, 'lunch/group_order_summary.html', context)
