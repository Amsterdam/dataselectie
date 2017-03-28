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

    token_default
    token_employee
    token_employee_plus
    """

    def setup_authorization(self):
        """
        SET

        token_default
        token_employee
        token_employee_plus

        to use with:

        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {}'.format(self.token_employee_plus))

        """
        # NEW STYLE AUTH
        key = settings.DATAPUNT_AUTHZ['JWT_SECRET_KEY']
        algorithm = settings.DATAPUNT_AUTHZ['JWT_ALGORITHM']
        jwt_ttl = settings.JWT_AUTH['JWT_EXPIRATION_DELTA']

        now = int(time.mktime(dt.now().timetuple()))
        expiry = int(time.mktime((dt.now() + jwt_ttl).timetuple()))

        token_default = jwt.encode({
            'authz': authorization_levels.LEVEL_DEFAULT,
            'iat': now, 'exp': expiry}, key, algorithm=algorithm)
        token_employee = jwt.encode({
            'authz': authorization_levels.LEVEL_EMPLOYEE,
            'iat': now, 'exp': expiry}, key, algorithm=algorithm)
        token_employee_plus = jwt.encode({
            'authz': authorization_levels.LEVEL_EMPLOYEE_PLUS,
            'iat': now, 'exp': expiry}, key, algorithm=algorithm)

        self.token_default = str(token_default, 'utf-8')
        self.header_auth_default = {AUTH_HEADER: f'Bearer {self.token_default}'}

        self.token_employee = str(token_employee, 'utf-8')
        self.header_auth_employee = {
            AUTH_HEADER: f'Bearer {self.token_employee}'}

        self.token_employee_plus = str(token_employee_plus, 'utf-8')
        self.header_auth_employee_plus = {
            AUTH_HEADER: f'Bearer {self.token_employee_plus}'}
