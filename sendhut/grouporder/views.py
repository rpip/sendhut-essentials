from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View

from sendhut.stores.models import Store
from .forms import GroupOrderForm
from .utils import (
    get_anonymous_group_order_token, create_group_order,
    set_group_order_cookie, join_group_order,
    join_group_order_anonymous, get_store_group_order_cookie_name
)
from .models import GroupOrder


def new_group_order(request):
    form = GroupOrderForm(data=request.POST)
    if form.is_valid():
        store_slug = form.cleaned_data['store']
        limit = form.cleaned_data['limit']
        store = Store.objects.get(slug=store_slug)
        create_group_order(request.user, store, limit)
        messages.info(request, "Group order created!")
        return redirect(reverse('stores:store_details', args=(store.slug,)))

    return redirect(request.META.get('HTTP_REFERER'))


class CartJoin(View):

    def get(self, request, *args, **kwargs):
        token = kwargs['ref']
        group_order = get_object_or_404(GroupOrder, token=token)
        next_url = reverse('stores:store_details', args=(group_order.store.slug,))
        response = redirect(next_url)
        if request.user.is_authenticated:
            # TODO(yao): switch carts between group order and regular modes
            join_group_order(request.user, group_order)
        else:
            member = get_anonymous_group_order_token(request, group_order.store)
            if not member:
                request.session['group_order'] = token
                # set anonymous cart cookie
                set_group_order_cookie(group_order, response)

        return response

    def post(self, request, *args, **kwargs):
        # join_group_order_anonymous(request, group_order, name)
        token = kwargs['ref']
        group_order = get_object_or_404(GroupOrder, token=token)
        name = request.POST.get('name')
        member = join_group_order_anonymous(request, group_order, name)
        next_url = reverse('stores:store_details', args=(group_order.store.slug,))
        response = redirect(next_url)
        set_group_order_cookie(group_order, response, member.cart.token)
        return response


def leave(request, ref):
    group_order = get_object_or_404(GroupOrder, token=ref)
    request.group_member.leave()
    fullname = group_order.user.get_full_name()
    msg = "You've been removed from {}'s cart".format(fullname)
    messages.info(request, msg)
    next_url = reverse('stores:store_details', args=(group_order.store.slug,))
    response = redirect(next_url)
    if not request.user.is_authenticated:
        cookie_name = get_store_group_order_cookie_name(group_order.store)
        response.delete_cookie(cookie_name)

    return response


def cancel(request, ref):
    group = GroupOrder.objects.get(token=ref)
    group.cancel()
    messages.info(request, "Group order deleted")
    return redirect(reverse('stores:store_details', args=(group.store.slug,)))


def rejoin(request, ref):
    group = get_object_or_404(GroupOrder, token=ref)
    group.find_member(request.user).join()
    return redirect(reverse('stores:store_details', args=(group.store.slug,)))
