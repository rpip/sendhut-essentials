from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View

from sendhut.lunch.models import Store
from .forms import GroupOrderForm
from .utils import create_group_order
from .models import GroupOrder


def new_group_order(request):
    form = GroupOrderForm(data=request.POST)
    if form.is_valid():
        store_slug = form.cleaned_data['store']
        limit = form.cleaned_data['limit']
        store = Store.objects.get(slug=store_slug)
        create_group_order(request.user, store, limit)
        messages.info(request, "Group order created!")
        return redirect(reverse('lunch:store_details', args=(store.slug,)))

    return redirect(request.META.get('HTTP_REFERER'))


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


def leave(request, ref):
    pass


def cancel(request, ref):
    group = GroupOrder.objects.get(token=ref)
    group.cancel()
    messages.info(request, "Group order deleted")
    return redirect(reverse('lunch:store_details', args=(group.store.slug,)))


def rejoin(request, ref):
    pass


def join(request, ref):
    pass
