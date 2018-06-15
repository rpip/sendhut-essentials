from django.conf.urls import url

from .views import giveaway_list, join_giveaway, leave_giveaway


urlpatterns = [
    url(r'^$', giveaway_list, name='list'),
    # sendhut.com/gifts/aK6798
    url(r'^(?P<code>[a-zA-Z0-9-]+)/leave$', leave_giveaway, name='leave'),
    url(r'^(?P<code>[a-zA-Z0-9-]+)$', join_giveaway, name='join'),
]
