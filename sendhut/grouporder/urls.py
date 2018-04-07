from django.conf.urls import url

from .views import new_group_order, leave, rejoin, cancel


urlpatterns = [
    url(r'^new/$', new_group_order, name='new'),
    url(r'^(?P<ref>[a-zA-Z0-9-]+)/leave/$', leave, name='leave'),
    url(r'^(?P<ref>[a-zA-Z0-9-]+)/rejoin/$', rejoin, name='rejoin'),
    url(r'^(?P<ref>[a-zA-Z0-9-]+)/cancel/$', cancel, name='cancel')
]
