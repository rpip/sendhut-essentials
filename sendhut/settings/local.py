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

# Email settings
EMAIL_PORT = 1025
EMAIL_HOST = 'localhost'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
