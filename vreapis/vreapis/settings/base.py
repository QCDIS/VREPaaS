'''
Django settings for vreapis project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
'''

from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = get_random_secret_key()

DEBUG = True

ALLOWED_HOSTS = ['localhost','127.0.0.1']

CSRF_TRUSTED_ORIGINS = ['http://localhost:3000']

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^http:\/\/localhost:\d+$',
]

KEYCLOAK_EXEMPT_URIS = []
#
KEYCLOAK_CONFIG = {
    'KEYCLOAK_SERVER_URL': os.getenv('KEYCLOAK_SERVER_URL'),
    'KEYCLOAK_REALM': os.getenv('KEYCLOAK_REALM'),
    'KEYCLOAK_CLIENT_ID': os.getenv('KEYCLOAK_CLIENT_ID'),
    'KEYCLOAK_CLIENT_SECRET_KEY': os.getenv('KEYCLOAK_CLIENT_SECRET_KEY')
}

# Application definition

INSTALLED_APPS = [
    'cells',
    'workflows',
    'virtual_labs',
    'data_products',
    'rest_framework',
    'rest_framework_gis',
    'rest_framework.authtoken',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django-keycloak-auth.middleware.KeycloakMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vreapis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vreapis.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": os.environ['DB_HOST'],
        "NAME": os.environ['DB_NAME'],
        "PASSWORD": os.environ['DB_PASSWORD'],
        "PORT": os.environ['DB_PORT'],
        "USER": os.environ['DB_USER'],
        }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

logg_level = os.getenv('LOG_LEVEL', 'WARNING')

LOGGING = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(name)s.%(funcName)s:%(lineno)s- %(message)s'
        },
    },

    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
            'formatter': 'simple',
        },
    },
}


BASE_PATH = os.environ.get('BASE_PATH', '').strip('/')

STATIC_URL = '/static/'
if BASE_PATH:
    STATIC_URL = f'{BASE_PATH}/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
