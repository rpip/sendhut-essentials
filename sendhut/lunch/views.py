from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Item, Basket


class FoodListView(ListView):

    model = Item
    context_object_name = 'items'

    def get_queryset(self):
        category = self.kwargs['category']
        return Basket.filter_by_category_slugs([category])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = Basket.format_slug(self.kwargs['category'])
        return context


class FoodDetailView(DetailView):

    model = Item
