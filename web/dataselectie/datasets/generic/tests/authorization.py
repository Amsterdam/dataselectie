import time
from datetime import datetime as dt

import jwt
from authorization_django import levels as authorization_levels
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
        # NEW STYLE AUTH
        key = settings.DATAPUNT_AUTHZ['JWT_SECRET_KEY']
        algorithm = settings.DATAPUNT_AUTHZ['JWT_ALGORITHM']
        jwt_ttl = settings.JWT_AUTH['JWT_EXPIRATION_DELTA']

        now = int(time.mktime(dt.now().timetuple()))
        expiry = int(time.mktime((dt.now() + jwt_ttl).timetuple()))

        token_default = jwt.encode({
            'scopes': [],
            'iat': now, 'exp': expiry}, key, algorithm=algorithm)
        token_scope_hr_r = jwt.encode({
            'scopes':[authorization_levels.SCOPE_HR_R],
            'iat': now, 'exp': expiry}, key, algorithm=algorithm)


        self.token_default = str(token_default, 'utf-8')
        self.header_auth_default = {AUTH_HEADER: f'Bearer {self.token_default}'}

        self.token_scope_hr_r = str(token_scope_hr_r, 'utf-8')
        self.header_auth_scope_hr_r = {
            AUTH_HEADER: f'Bearer {self.token_scope_hr_r}'}
