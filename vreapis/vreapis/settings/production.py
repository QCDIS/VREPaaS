from vreapis.settings.base import *


DEBUG = False

ALLOWED_HOSTS = ["lfw-ds001-i022.lifewatch.dev"]

CSRF_TRUSTED_ORIGINS = ['https://lfw-ds001-i022.lifewatch.dev:32443']

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https:\/\/lfw-ds001-i022.lifewatch.dev:\d+$',
]

FORCE_SCRIPT_NAME = '/vre-api/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

WHITENOISE_STATIC_PREFIX = '/static/'
STATIC_URL = '/vre-api' + WHITENOISE_STATIC_PREFIX
STATIC_ROOT = BASE_DIR / "staticfiles"