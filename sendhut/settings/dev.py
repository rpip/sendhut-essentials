from .base import *

"""
The in-development settings and the default configuration.
"""
INTERNAL_IPS = [
    '127.0.0.1'
]

MIDDLEWARE = MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]
