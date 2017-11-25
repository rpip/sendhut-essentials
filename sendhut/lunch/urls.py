from django.conf.urls import url
from .views import FoodListView, DetailView

urlpatterns = [
    url(r'^(?P<category>[a-zA-Z0-9-]+)/$',
        FoodListView.as_view(), name='food_list')
]
