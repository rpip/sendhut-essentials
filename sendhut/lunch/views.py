import json

from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from djmoney.money import Money

from .models import Item, Basket
from sendhut.cart import Cart
from sendhut import utils


class FoodListView(ListView):

    model = Item
    context_object_name = 'items'
    ITEMS_PER_PAGE = 30
    template_name = 'lunch/item_list.html'

    def get_queryset(self):
        category = self.kwargs['category']
        items = Basket.filter_by_category_slugs([category])
        paginator = Paginator(items, self.ITEMS_PER_PAGE)
        page = self.request.GET.get('page', 1)
        items = paginator.page(page)
        # if self.request.is_ajax(), return ajax list view
        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = category = self.kwargs['category']
        context['page_title'] = Basket.format_slug(category)
        return context


class FoodDetailView(DetailView):

    model = Item
    context_object_name = 'item'
    template_name = 'lunch/_item_detail.html'

    def get_object(self):
        # category_slug = self.kwargs['category']
        slug = self.kwargs['slug']
        return Item.objects.get(slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = context['item'].name
        context['category'] = self.kwargs['category']
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
        _hash = self.kwargs['hash']
        cart = Cart(self.request)
        context['cart_line'] = cart.get_line_by_hash(_hash).serialize()
        return context


class CartLineDeleteView(View):
    def post(self, request, *args, **kwargs):
        _hash = self.kwargs['hash']
        cart = Cart(self.request)
        Cart(request).remove_by_hash(_hash)
        return JsonResponse({'status': 'OK'}, encoder=utils.JSONEncoder)


class CartView(View):
    # TODO(yao): implement dynamic delivery cost calculation

    def get(self, request):
        # /cart
        if request.GET.get('clear'):
            Cart(request).clear()

        return render(request, 'partials/cart.html', self._get_cart())

    def post(self, request):
        # /cart
        cart = Cart(request)
        data = json.loads(request.body)
        item = Item.objects.get(uuid=data['uuid'])
        quantity = data.pop('quantity')
        # import pdb; pdb.set_trace()
        cart.add(item, int(quantity), data)
        # print("Item {}\n Qty {}\n Data {}".format(item, quantity, data))
        return JsonResponse(self._get_cart(), encoder=utils.JSONEncoder)

    def _get_cart(self):
        cart = Cart(self.request)
        delivery_fee = Money(200, 'NGN')
        sub_total = Money(cart.get_subtotal(), 'NGN')
        total = sub_total + delivery_fee
        return {
            'cart': cart.serialize(),
            'sub_total': sub_total,
            'delivery_fee': delivery_fee,
            'total': total
        }


class CheckOutView(CartView):
    # TODO(yao): refresh cart on item add
    # TODO(yao):
    def get(self, request, *args, **kwargs):
        return render(request, 'lunch/confirm_checkout.html', self._get_cart())

    def post(self, request, *args, **kwargs):
        pass


def order_history(request):
    pass
