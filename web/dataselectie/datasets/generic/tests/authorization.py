import time
from datetime import datetime as dt

import jwt
from authorization_django.config import settings as middleware_settings
import authorization_levels
from django.conf import settings

AUTH_HEADER = 'HTTP_AUTHORIZATION'


class AuthorizationSetup(object):
    """
    Helper methods to setup JWT tokens and authorization levels

    sets the following attributes:

    token_scope_hr_r
    """

    def setup_authorization(self):
        """
        SET

        token_scope_hr_r

        to use with:

        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_scope_hr_r))

        """
        # VERY NEW STYLE AUTH. JWKS public/private keys are defined in settings
        jwks = middleware_settings()['JWKS'].signers

        assert len(jwks) > 0
        (kid, key), = jwks.items()

        now = int(time.time())

        token_default = jwt.encode({
            'scopes': [],
            'iat': now, 'exp': now + 600}, key.key, algorithm=key.alg,headers={'kid': kid})
        token_scope_hr_r = jwt.encode({
            'scopes':[authorization_levels.SCOPE_HR_R],
            'iat': now, 'exp': now + 600}, key.key, algorithm=key.alg,headers={'kid': kid})

        self.token_default = str(token_default, 'utf-8')
        self.header_auth_default = {AUTH_HEADER: f'Bearer {self.token_default}'}

        self.token_scope_hr_r = str(token_scope_hr_r, 'utf-8')
        self.header_auth_scope_hr_r = {
            AUTH_HEADER: f'Bearer {self.token_scope_hr_r}'}
