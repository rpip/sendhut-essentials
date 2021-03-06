import os
from pathlib import Path
from urllib.parse import urlparse
from django.contrib.messages import constants as messages

from decouple import config, Csv
import dj_database_url
import dj_email_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent.parent.parent

ENV = config('ENVIRONMENT')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

TEMPLATE_DEBUG = config('TEMPLATE_DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='*')

SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    'debug_toolbar',
    'storages',
    'djmoney',
    'django_rq',
    'taggit',
    'sorl.thumbnail',
    'widget_tweaks',
    'templated_email',
    'safedelete',
    'rest_framework',
    'multiupload',
    'nested_admin',
    'loginas',

    'sendhut',
    'sendhut.accounts',
    'sendhut.stores',
    'sendhut.cart',
    'sendhut.grouporder',
    'sendhut.checkout'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'sendhut.middleware.site',
    'sendhut.middleware.cart',
]

ROOT_URLCONF = 'sendhut.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': TEMPLATE_DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'sendhut.cart.context_processors.cart',
                'sendhut.context_processors.default_currency',
                'sendhut.context_processors.mobile_check',
                'sendhut.context_processors.food_tags',
                'sendhut.context_processors.delivery_schedule',
                'sendhut.context_processors.base_configs',
                'sendhut.grouporder.context_processors.group_order'
            ],
        },
    },
]

WSGI_APPLICATION = 'sendhut.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default':  dj_database_url.config(
        default=config(
            'DATABASE_URL',
            default='sqlite:///{}'.format(Path(BASE_DIR, 'db.sqlite3'))
        ),
        engine='django.contrib.gis.db.backends.postgis',
        conn_max_age=500,
    )
}

# TODO(yao): setup PostGIS Heroku https://devcenter.heroku.com/articles/python-c-deps#geodjango-application-libraries
GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')
GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH')

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    'sendhut.auth_backends.UsernamePhoneAuthentication',
    #'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'en-ngn'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    Path(BASE_DIR, "static/dist")
]

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home2/media/media.lawrence.com/media/"
MEDIA_ROOT = Path(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/"
MEDIA_URL = '/media/'

AUTH_USER_MODEL = 'accounts.User'

REDIS_URL = urlparse(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

# CACHING
# ---------------------------------------------------------------
CACHES = {
    "default": {
         "BACKEND": "redis_cache.RedisCache",
         "LOCATION": "{0}:{1}".format(REDIS_URL.hostname, REDIS_URL.port),
         "OPTIONS": {
             "PASSWORD": REDIS_URL.password,
             "DB": 0,
         }
    }
}


CART_SESSION_ID = 'cart'

GROUP_CART_SESSION_ID = 'group_orders'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


DEFAULT_CURRENCY = 'NGN'

BASE_DELIVERY_FEE = 600

SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='hello@sendhut.com')

BETA_MODE = config('BETA_MODE', default=True, cast=bool)

BETA_MESSAGE = config('BETA_MESSAGE', default="We're not quite ready yet, but we'd love you to give it a try. \
If you spot any glitches please let us know on phone 08169567963 or email hello@sendhut.com")

LOGIN_URL = '/login'

PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')

PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY')

REDIS_URL = urlparse(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

# solr-thumbnail related settings
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
THUMBNAIL_REDIS_HOST = REDIS_URL.hostname
THUMBNAIL_REDIS_PORT = REDIS_URL.port
# THUMBNAIL_DEBUG = True

# Email settings
# EMAIL_URL = config('EMAIL_URL', default='console://')

# email_config = dj_email_url.parse(EMAIL_URL)

# EMAIL_FILE_PATH = email_config['EMAIL_FILE_PATH']
# EMAIL_HOST_USER = email_config['EMAIL_HOST_USER']
# EMAIL_HOST_PASSWORD = email_config['EMAIL_HOST_PASSWORD']
# EMAIL_HOST = email_config['EMAIL_HOST']
# EMAIL_PORT = email_config['EMAIL_PORT']
# EMAIL_BACKEND = email_config['EMAIL_BACKEND']
# EMAIL_USE_TLS = email_config['EMAIL_USE_TLS']
# EMAIL_USE_SSL = email_config['EMAIL_USE_SSL']

EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = 'key-aae710e87fcc0a628b1fc9fbface936e'
MAILGUN_SERVER_NAME = 'mg.sendhut.com'

# TODO(yao): personalize email with 'Yao from Sendhut'
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Sendhut <hello@sendhut.com>')

# SMS
JUSIBE_PUBLIC_KEY = "a21e294d898ca47299bd575e5db983dd"
JUSIBE_ACCESS_TOKEN = "8dcdee5ff5d7504570ffb0d74e1fc755"

SESSION_SERIALIZER = 'sendhut.utils.JSONSerializer'

DEFAULT_DOMAIN = config('DEFAULT_DOMAIN', default='food.sendhut.com')

RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL.geturl(),
        'DEFAULT_TIMEOUT': 500,
        'USE_REDIS_CACHE': 'redis-cache',
    }
}

RQ_SHOW_ADMIN_LINK = True

ENABLE_SSL = False

DEFAULT_CURRENCY = "NGN"

try:
    site = Site.objects.get_current()
    site.name = 'Sendhut'
    site.domain = DEFAULT_DOMAIN
    site.save()
except:
    pass


GOOGLE_MAPS_API_KEY = 'AIzaSyDVZn9gbIfivvhXOI1eAY1tu2M-yo2LO9w'

GROUP_ORDER_MESSAGE = "You can order in lunch with coworkers or friends with the group order."

FOOD_CONTAINER_CHARGE = 1.50
