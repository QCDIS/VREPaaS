import os

from vreapis.settings.base import *


DEBUG = False

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOST')]
CSRF_TRUSTED_ORIGINS = [os.getenv('TRUSTED_ORIGINS')]

CORS_ALLOWED_ORIGIN_REGEXES = [
    os.getenv('CORS_ALLOWED_ORIGIN_REGEXES'),
]

FORCE_SCRIPT_NAME = '/vre-api/'

WHITENOISE_STATIC_PREFIX = '/static/'
STATIC_URL = '/vre-api' + WHITENOISE_STATIC_PREFIX
STATIC_ROOT = BASE_DIR / "staticfiles"