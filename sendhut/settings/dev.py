from .base import *
from django.contrib.messages import constants as message_constants

INTERNAL_IPS = [
    '127.0.0.1'
]

MIDDLEWARE = MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

MESSAGE_LEVEL = message_constants.DEBUG

# # Security
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000)
# SECURE_REDIRECT_EXEMPT = config('SECURE_REDIRECT_EXEMPT', cast=Csv)
# SECURE_SSL_HOST = config('SECURE_SSL_HOST')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True)
SECURE_PROXY_SSL_HEADER = config(
    'SECURE_PROXY_SSL_HEADER',
    default=('HTTP_X_FORWARDED_PROTO', 'https')
)

# Static and Media
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'sendhut-assets'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_STATIC_LOCATION = 'static'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)
STATICFILES_STORAGE = 'sendhut.storage_backends.StaticStorage'

DEFAULT_FILE_STORAGE = 'sendhut.storage_backends.MediaStorage'
AWS_PUBLIC_MEDIA_LOCATION = 'media/public'

EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=1025)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
DEFAULT_FROM_EMAIL = 'hello@sendhut.com'
