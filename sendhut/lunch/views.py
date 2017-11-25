from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Item, Basket


class FoodListView(ListView):

    model = Item

    def get_queryset(self):
        category = self.kwargs['category']
        return Basket.filter_by_category_slugs([category])


class FoodDetailView(DetailView):

    model = Item
