from urllib.parse import urljoin
from datetime import datetime
from functools import singledispatch
from enum import Enum
import json
import os
import hashlib
import binascii
import re

from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.contrib.sites.models import Site

from faker import Faker
import redis
from djmoney.money import Money
from django.core.serializers.json import DjangoJSONEncoder


MOBILE_AGENT_RE = re.compile(r".*(iphone|ios|mini|mobile|androidtouch)", re.IGNORECASE)

REDIS = redis.StrictRedis(
    host=settings.REDIS_URL.hostname,
    port=settings.REDIS_URL.port,
    password=settings.REDIS_URL.password)


def sane_repr(*attrs):
    if 'id' not in attrs and 'pk' not in attrs:
        attrs = ('id', ) + attrs

    def _repr(self):
        cls = type(self).__name__

        pairs = ('%s=%s' % (a, repr(getattr(self, a, None))) for a in attrs)

        return u'<%s at 0x%x: %s>' % (cls, id(self), ', '.join(pairs))

    return _repr


def image_upload_path(instance, filename):
    import os
    from django.utils.timezone import now
    filename_base, filename_ext = os.path.splitext(filename)

    return 'foods/%s%s' % (
        now().strftime("%Y%m%d%H%M%S"),
        filename_ext.lower()
    )


def generate_token(token_length=16):
    "Returns a random hexadecimal string with the given length."
    token = binascii.b2a_hex(os.urandom(token_length))[:token_length]
    return token.decode('utf-8')


def hash_data(data, hash_length=190, data_type=None):
    salt = "ValentinaIsTheMostAwsomeDogInTheWord"
    if data:
        data = "{}{}".format(data, salt)
        data_hashed = hashlib.sha512(data.encode('utf-8')).hexdigest()
        data_hashed = data_hashed[0:hash_length]
    else:
        data_hashed = None
    return data_hashed


def generate_random_name():
    fake = Faker()
    token = generate_token()
    word = '{}-{}-{}'.format(token, fake.color_name(), fake.street_name())
    return word.replace(' ', '-')


def unslugify(text):
    return text.replace('-', ' ').replace('_', ' ')


def is_mobile(request):
    """Return True if the request comes from a mobile device."""
    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False


def generate_password_token(email):
    token = generate_token(13)
    REDIS.setex(token, 60 * 5, email)
    return token


def check_password_token(token):
    return REDIS.get(token)


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)


@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


@to_serializable.register(datetime)
def ts_datetime(val):
    """Used if *val* is an instance of datetime."""
    return val.isoformat() + "Z"


@to_serializable.register(Money)
def ts_money(val):
    """Used if *val* is an instance of Money."""
    return val.amount


class JSONSerializer:
    """
    Simple wrapper around json for session serialization
    """
    def dumps(self, obj):
        serialized = json.dumps(obj, separators=(',', ':'), default=to_serializable)
        return serialized.encode('latin-1')

    def loads(self, data):
        return json.loads(data.decode('latin-1'))


class JSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except:
            return json_encode(obj)


def json_encode(data):
    return json.dumps(data, default=to_serializable)


def build_absolute_uri(location):
    # type: (str, bool, saleor.site.models.SiteSettings) -> str
    host = Site.objects.get_current().domain
    protocol = 'https' if settings.ENABLE_SSL else 'http'
    current_uri = '%s://%s' % (protocol, host)
    location = urljoin(current_uri, location)
    return iri_to_uri(location)
