from django.conf.urls import url

from .views import claim_coupon


urlpatterns = [
    # sendhut.com/gifts/aK6798
    url(r'^(?P<code>[a-zA-Z0-9-]+)$', claim_coupon, name='redeem'),
]
