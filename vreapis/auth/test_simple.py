from django.test import TestCase, RequestFactory
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

from auth.simple import StaticTokenAuthentication


class StaticTokenAuthenticationTestCase(TestCase):
    tokens_accepted = [f'Token {settings.NAAVRE_API_TOKEN}', ]
    tokens_not_accepted = [f'{settings.NAAVRE_API_TOKEN}', f'', f'0123456789abcdef0123456789abcdef01234567', ]

    def test_authenticate(self):
        request_factory = RequestFactory()
        authenticator = StaticTokenAuthentication()
        print(StaticTokenAuthenticationTestCase.tokens_accepted)
        for token in StaticTokenAuthenticationTestCase.tokens_accepted:
            request = request_factory.post('', HTTP_AUTHORIZATION=token)
            user, _ = authenticator.authenticate(request)
        for token in StaticTokenAuthenticationTestCase.tokens_not_accepted:
            request = request_factory.post('', HTTP_AUTHORIZATION=token)
            self.assertRaises(AuthenticationFailed, authenticator.authenticate, request)
