import json
import os
import hashlib
import binascii

from faker import Faker

from djmoney.money import Money
from django.core.serializers.json import DjangoJSONEncoder


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
    " Returns a random hexadecimal string with the given length."
    token = binascii.b2a_hex(os.urandom(token_length))[:token_length]
    return token.decode('utf-8')


class JSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Money):
            return obj.amount
        return super().default(obj)


def json_encode(data):
    return json.dumps(data, cls=JSONEncoder)


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
