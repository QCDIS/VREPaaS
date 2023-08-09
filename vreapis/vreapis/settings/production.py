import os

from vreapis.settings.base import *


DEBUG = False

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOST')]
CSRF_TRUSTED_ORIGINS = [os.getenv('TRUSTED_ORIGINS')]

CORS_ALLOWED_ORIGIN_REGEXES = [
    os.getenv('CORS_ALLOWED_ORIGIN_REGEXES'),
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# URL path

FORCE_SCRIPT_NAME = os.getenv('URL_PATH')
WHITENOISE_STATIC_PREFIX = '/static/'
STATIC_URL = os.getenv('URL_PATH') + WHITENOISE_STATIC_PREFIX
STATIC_ROOT = BASE_DIR / "staticfiles"
