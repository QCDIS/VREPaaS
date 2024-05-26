from django.test import TestCase, RequestFactory
from django.conf import settings
from urllib.parse import urlencode
from auth.Keycloak import KeycloakAuthentication
import common


class KeycloakAuthenticationTestCase(TestCase):
    def test_authenticate(self):  # todo. what if authentication failed? what if refresh token is used?
        post_data: dict[str, str] = {'client_id': settings.KEYCLOAK_CLIENT_ID, 'grant_type': 'password', 'scope': 'openid', 'username': 'u', 'password': 'u'}
        response_body: dict[str, any] = common.session.post(settings.KEYCLOAK_LOGIN_URL, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=urlencode(post_data), verify=settings.ALLOW_INSECURE_TLS).json()
        access_token: str = response_body['access_token']

        request_factory = RequestFactory()
        request = request_factory.post('', HTTP_AUTHORIZATION=access_token)
        authenticator = KeycloakAuthentication()
        user, _ = authenticator.authenticate(request)
        assert user.username == post_data['username']
