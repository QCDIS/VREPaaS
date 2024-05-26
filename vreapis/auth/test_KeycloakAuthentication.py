from django.test import TestCase, RequestFactory
from django.conf import settings
from urllib.parse import urlencode
from auth.Keycloak import KeycloakAuthentication
from django.contrib.auth.models import User
import common


class KeycloakAuthenticationTestCase(TestCase):
    def test_authenticate(self):
        post_data: dict[str, str] = {'client_id': 'myclient', 'grant_type': 'password', 'scope': 'openid', 'username': 'u', 'password': 'u'}
        response_body = common.session.post(settings.KEYCLOAK_LOGIN_URL, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=urlencode(post_data), verify=settings.ALLOW_INSECURE_TLS).json()
        access_token = response_body['access_token']

        request_factory = RequestFactory()
        request = request_factory.post('', HTTP_AUTHORIZATION=access_token)
        authenticator = KeycloakAuthentication()
        user, _ = authenticator.authenticate(request)
        assert user.username == post_data['username']
