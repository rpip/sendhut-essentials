import os
import binascii


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


def generate_token(token_length=19):
    " Returns a random hexadecimal string with the given length."
    return binascii.b2a_hex(os.urandom(token_length))[:token_length]
