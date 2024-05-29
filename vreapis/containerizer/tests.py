import json
from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth.models import User
from urllib.parse import urlencode
import requests


class ContainerizerTestCase(TestCase):
    @staticmethod
    def Keycloak_login() -> dict[str, any]:
        return requests.post(settings.KEYCLOAK_LOGIN_URL, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=urlencode({'client_id': 'myclient', 'grant_type': 'password', 'scope': 'openid', 'username': 'u', 'password': 'u'}), verify=settings.ALLOW_INSECURE_TLS).json()

    def test_get_base_images(self):
        client = Client()
        dummy_username = f'test'
        dummy_password = '0'
        try:
            dummy_user: User = User.objects.get(username=dummy_username)
        except User.DoesNotExist:
            dummy_user = User.objects.create_user(dummy_username, password=dummy_password)
        client.login(username=dummy_username, password=dummy_password)

        response = client.get('/api/containerizer/baseimagetags/')
        self.assertEqual(response.status_code, 200)
        images = response.json()
        self.assertIsInstance(images, dict)
        self.assertGreater(len(images), 0)
