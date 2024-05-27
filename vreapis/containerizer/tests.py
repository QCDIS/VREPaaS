import os
from django.test import TestCase, Client
from django.conf import settings
from urllib.parse import urlencode
import requests


class ContainerizerTestCase(TestCase):
    @staticmethod
    def Keycloak_login() -> dict[str, any]:
        return requests.post(settings.KEYCLOAK_LOGIN_URL, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=urlencode({'client_id': 'myclient', 'grant_type': 'password', 'scope': 'openid', 'username': 'u', 'password': 'u'}), verify=settings.ALLOW_INSECURE_TLS).json()

    def test_get_base_images(self):
        client = Client()

        login_inf = ContainerizerTestCase.Keycloak_login()
        response = client.post()