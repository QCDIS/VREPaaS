import os

from vreapis.settings.base import *


DEBUG = False

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOST')]

CORS_ALLOWED_ORIGIN_REGEXES = [
    os.getenv('CORS_ALLOWED_ORIGIN_REGEXES'),
]
