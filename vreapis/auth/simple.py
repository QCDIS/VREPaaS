from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.conf import settings
import string
import random


class StaticTokenAuthentication(BaseAuthentication):
    dummy_user: User

    def __init__(self):
        try:
            StaticTokenAuthentication.dummy_user = User.objects.get(username=settings.NAAVRE_API_TOKEN)
        except User.DoesNotExist:
            StaticTokenAuthentication.dummy_user = User.objects.create_user(settings.NAAVRE_API_TOKEN, password=''.join(random.choice(string.printable) for _ in range(32)))

    def authenticate(self, request: HttpRequest):
        access_token: str = request.headers.get('Authorization', '')
        print(access_token == f'Token {settings.NAAVRE_API_TOKEN}')
        if access_token != f'Token {settings.NAAVRE_API_TOKEN}':
            raise AuthenticationFailed(f'Invalid NaaVRE API token')
        return StaticTokenAuthentication.dummy_user, None
