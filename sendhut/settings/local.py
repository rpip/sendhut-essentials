from .base import *
from django.contrib.messages import constants as message_constants

"""
The in-development settings and the default configuration.
"""
INTERNAL_IPS = [
    '127.0.0.1'
]

MIDDLEWARE = MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

MESSAGE_LEVEL = message_constants.DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
