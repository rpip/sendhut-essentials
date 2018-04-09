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
from django.conf import settings
from django.db.models import Q

from sendhut import notifications, payments, utils
from sendhut.cart.utils import get_cart_data
from sendhut.grouporder.utils import get_anonymous_group_order_token
from sendhut.grouporder.models import Member, GroupOrder
from .models import Item, Store, Order, FOOD_TAGS
from .forms import CheckoutForm, PartnerSignupForm


def food_detail(request, slug):
    template = 'lunch/_item_detail.html'
    item = Item.objects.get(slug=slug)
    context = {
        'item': item,
        'page_title': item.name,
    }
    return render(request, template, context)


def cartline_detail(request, line_id, slug):
    template = 'lunch/_item_detail.html'
    item = Item.objects.get(slug=slug)
    context = {
        'item': item,
        'page_title': item.name,
    }
    cart = request.cart
    context['cart_line'] = cart.lines.get(id=line_id)
    return render(request, template, context)


def cartline_delete(request, line_id):
    cart = request.cart
    cart.remove_line(line_id)
    return JsonResponse({'status': 'OK'})


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
    orders = Order.objects.filter(user=request.user)
    return render(
        request,
        'lunch/order_history.html',
        {'orders': orders, 'open_carts': []}
    )


@login_required
def order_details(request, ref):
    context = {
        'order': get_object_or_404(Order, user=request.user, reference=ref)
    }
    return render(request, 'lunch/order_details.html', context)


def store_page(request, slug):
    template = 'lunch/store_details.html'
    store = get_object_or_404(Store, slug=slug)
    context = {
        'store': store,
        'page_title': store.name
    }
    if not request.group_member:
        token = get_anonymous_group_order_token(request, store)
        if token:
            member = Member.objects.filter(cart__token=token).first()
            if not member:
                group_token = request.session['group_order']
                try:
                    group_order = GroupOrder.objects.get(token=group_token)
                    context['anonymous_group_join'] = True
                    context['group_order'] = group_order
                except GroupOrder.DoesNotExist:
                    pass

    if not request.group_member:
        messages.info(request, settings.GROUP_ORDER_MESSAGE)

    return render(request, template, context)


class CartView(View):
    # TODO(yao): implement dynamic delivery cost calculation

    def get(self, request):
        cart = request.cart
        context = get_cart_data(cart)
        return render(request, 'partials/sidebar_cart.html', context)

    def post(self, request):
        "This endpoints handle new cart additions and cart item updates"
        data = json.loads(request.body)
        cart = request.cart
        item = Item.objects.get(uuid=data['uuid'])
        quantity = data.pop('quantity')
        # if line_id is present, it means it's an update
        cart.add(item, int(quantity), data, replace=bool(data.get('line_id')))
        return JsonResponse(get_cart_data(cart), encoder=utils.JSONEncoder)


def cart_reload(request):
    template = 'lunch/cart_summary.html'
    return render(request, template)


class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        form = CheckoutForm(data=request.POST)
        context = get_cart_data(request.cart)
        context['form'] = form
        return render(request, 'lunch/cart_summary.html', context)

    def post(self, request):
        form = CheckoutForm(data=request.POST)
        cart = request.cart
        if not(form.is_valid()):
            messages.error(request, "Please complete the delivery form to proceed")
            context = get_cart_data(cart)

            return render(request, 'lunch/cart_summary.html', context)

        cash_delivery = form.cleaned_data.pop('cash_delivery')
        # TODO(yao): send invoice email, send sms confirmation/updates
        _cart = cart.build_cart()
        user = request.user
        # from django.db import IntegrityError
        order = Order.create_from_cart(
            cart=cart,
            user=user,
            total_cost=_cart['total'],
            delivery_fee=_cart['delivery_fee'],
            **form.cleaned_data
        )
        # TODO(yao): also notify group cart owner participants
        notifications.send_order_confirmation(user.email, order)

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

        return redirect('home')
