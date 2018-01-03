import json

from django.views import View
from django.views.generic.detail import DetailView
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Item, Partner, Order, OrderLine
from sendhut.cart import Cart
from sendhut import utils


def restaurant_menu(request, slug):
    messages.info(request, "You can order in lunch with coworkers or \
    friends with the group order.")
    template = 'lunch/restaurant_menu.html'
    vendor = get_object_or_404(Partner, slug=slug)
    context = {
        'vendor': vendor
    }
    return render(request, template, context)


class FoodDetailView(DetailView):

    model = Item
    context_object_name = 'item'
    template_name = 'lunch/_item_detail.html'

    def get_object(self):
        slug = self.kwargs['slug']
        return Item.objects.get(slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = context['item'].name
        return context


class CartLineDetailView(DetailView):

    model = Item
    context_object_name = 'item'
    template_name = 'lunch/_item_detail.html'

    def get_object(self):
        slug = self.kwargs['slug']
        return Item.objects.get(slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = context['item'].name
        uuid = self.kwargs['uuid']
        cart = Cart(self.request)
        context['cart_line'] = cart.get_line(uuid).serialize()
        return context


class CartLineDeleteView(View):
    def post(self, request, *args, **kwargs):
        uuid = self.kwargs['uuid']
        Cart(request).remove(uuid)
        return JsonResponse({'status': 'OK'}, encoder=utils.JSONEncoder)


class CartView(View):
    # TODO(yao): implement dynamic delivery cost calculation

    def get(self, request):
        # /cart
        if request.GET.get('clear'):
            Cart(request).clear()

        cart = Cart(request).build_cart()
        return render(request, 'partials/sidebar_cart.html', cart)

    def post(self, request):
        # /cart
        cart = Cart(request)
        data = json.loads(request.body)
        item = Item.objects.get(uuid=data['uuid'])
        quantity = data.pop('quantity')
        cart.add(item, int(quantity), data)
        return JsonResponse(cart.build_cart(), encoder=utils.JSONEncoder)


class DeliveryTimeView(CartView):
    def post(self, request, *args, **kwargs):
        delivery_time = self.request.POST['delivery_time']
        Cart(request).set_delivery_time(delivery_time)
        return JsonResponse(self._get_cart(), encoder=utils.JSONEncoder)


def cart_summary(request):
    cart = Cart(request).build_cart()
    return render(request, 'lunch/cart_summary.html', cart)


def cart_reload(request):
    cart = Cart(request).build_cart()
    return render(request, 'lunch/_cart_summary.html', cart)


def list_orders(request):
    pass


class CheckoutView(LoginRequiredMixin, View):

    def post(self, request):
        delivery_address = request.POST.get('delivery_address')
        if not(delivery_address):
            messages.error(request, "Provide delivery address")
        delivery_time = request.POST.get('delivery_time')
        notes = request.POST.get('notes')
        cart = Cart(request)
        # TODO(yao): email cart
        _cart = cart.build_cart()
        order = Order.objects.create(
            user=request.user,
            delivery_time=delivery_time,
            notes=notes,
            delivery_address=delivery_address,
            delivery_fee=_cart['delivery_fee']
        )
        for line in cart:
            data = cart.serialized()
            OrderLine.objects.create(
                item_id=line.item_id,
                quantity=line.get_quantity(),
                price=line.get_total(),
                order=order,
                special_instructions=data['note'],
                metadata=data
            )
        cart.clear()
        messages.info(request, "Order submitted for processing. reference {}".format(order.reference))
        return redirect('home')
