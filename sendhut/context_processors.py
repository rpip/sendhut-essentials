from django.conf import settings

from sendhut.checkout.models import Order
from sendhut.stores.models import FOOD_TAGS
from sendhut import utils


def get_setting_as_dict(name, short_name=None):
    short_name = short_name or name
    try:
        return {short_name: getattr(settings, name)}
    except AttributeError:
        return {}


# request is a required parameter
# pylint: disable=W0613
def default_currency(request):
    return get_setting_as_dict('DEFAULT_CURRENCY')


def mobile_check(request):
    return {'is_mobile': utils.is_mobile(request)}


def food_tags(request):
    return {'food_tags': FOOD_TAGS.labels()}


def delivery_schedule(request):
    return {
        'delivery_schedule': Order.DELIVERY_TIMES,
        'BASE_DELIVERY_FEE': settings.BASE_DELIVERY_FEE
    }


def vendor_configs(request):
    return {
        'PAYSTACK_PUBLIC_KEY': settings.PAYSTACK_PUBLIC_KEY,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }

# TODO(yao): add delivery fee context processor
