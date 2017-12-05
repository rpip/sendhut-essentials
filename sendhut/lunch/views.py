import json
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Item, Basket
from sendhut.cart import Cart


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
        return context


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
        cart.add(item, int(quantity), data)
        return JsonResponse(self._get_cart())

    def delete(self, request, *args, **kwargs):
        # DELETE /cart/id
        item = Item.objects.get(id=kwargs['id'])
        Cart(request).remove(item)
        return JsonResponse(self._get_cart())

    def _get_cart(self):
        cart = Cart(self.request)
        delivery_fee = 200
        sub_total = cart.get_subtotal()
        total = sub_total + delivery_fee
        return {
            'cart': cart.serialize(),
            'sub_total': sub_total,
            'delivery_fee': delivery_fee,
            'total': total
        }


class CheckOutView(View):

    def get(self, request, *args, **kwargs):
        pass


class OrderHistoryView(View):

    def get(self, request, *args, **kwargs):
        pass


class PaymentView(View):

    def get(self, request, *args, **kwargs):
        pass
