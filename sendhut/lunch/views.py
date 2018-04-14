import json
from functools import reduce
import operator

from django.views import View
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q

from sendhut import utils
from sendhut.cart.utils import get_cart_data
from sendhut.grouporder.utils import (
    get_anonymous_group_order_token, get_active_user_group_orders
)
from sendhut.grouporder.models import Member, GroupOrder
from sendhut.checkout.models import Order
from .models import Item, Store, FOOD_TAGS


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


def store_page(request, slug):
    template = 'lunch/store_details.html'
    store = get_object_or_404(Store, slug=slug)
    context = {
        'store': store,
        'page_title': store.name
    }
    # TODO(yao): refactor redirect afer anonymous user joins group
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
        # TODO(yao): prevent adding to locked group order carts
        # if line_id is present, it means it's an update
        cart.add(item, int(quantity), data, replace=bool(data.get('line_id')))
        return JsonResponse(get_cart_data(cart), encoder=utils.JSONEncoder)


def cart_reload(request):
    template = 'checkout/cart_summary.html'
    return render(request, template)


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    active_group_orders = get_active_user_group_orders(request.user)
    return render(
        request,
        'lunch/order_history.html',
        {'orders': orders, 'active_group_orders': active_group_orders}
    )


@login_required
def order_details(request, ref):
    context = {
        'order': Order.objects.get(user=request.user, reference=ref)
    }
    return render(request, 'lunch/order_details.html', context)
