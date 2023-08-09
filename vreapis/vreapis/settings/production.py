import os

from vreapis.settings.base import *


DEBUG = False

ALLOWED_HOSTS = ['localhost','127.0.0.1',os.getenv('ALLOWED_HOST')]
CSRF_TRUSTED_ORIGINS = [os.getenv('TRUSTED_ORIGINS')]

CORS_ALLOWED_ORIGIN_REGEXES = [
    os.getenv('CORS_ALLOWED_ORIGIN_REGEXES'),
]
