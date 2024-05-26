import os
from requests.exceptions import RequestException
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.conf import settings
import jwt
import jwt.algorithms

import common


class KeycloakAuthentication(BaseAuthentication):
    def authenticate(self, request: HttpRequest):
        received_token: str = request.headers.get('Authorization', '')
        if received_token == '':
            raise AuthenticationFailed('Authorization header not found. Login using Keycloak to get an access token.')
        token_header: dict[str, any] = jwt.get_unverified_header(received_token)
        try:
            verif_body: dict[str, any] = common.session.get(settings.KEYCLOAK_VERIF_URL, verify=settings.ALLOW_INSECURE_TLS).json()
        except RequestException as e:
            common.logger.error(f'Internal server error while getting Keycloak public key.')
            return None
        kid: str = token_header.get('kid', '')
        if kid == '':
            common.logger.error(f'JWT Key ID (kid) not found:{os.linesep}{received_token}')
            raise AuthenticationFailed(f'Invalid token format: JWT Key ID (kid) not found.')
        verif_keys: list[dict[str, any]] = verif_body.get('keys', [])
        key = next((key for key in verif_keys if key['kid'] == kid), None)
        if key is None:
            common.logger.error(f'Keycloak public key not found.')
            return None
        pub_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        access_token: dict[str, any] = jwt.decode(received_token, pub_key, algorithms=key['alg'], audience='account')
        username: str = access_token.get('preferred_username', '')
        if username == '':
            common.logger.error(f'Username (preferred_username) not found in token:{os.linesep}{received_token}')
            raise AuthenticationFailed(f'Invalid token format: Username (preferred_username) not found.')
        try:
            user: User | None = User.objects.get(username=username)
        except User.DoesNotExist:
            user: User = User.objects.create_user(username)
        return user, None
