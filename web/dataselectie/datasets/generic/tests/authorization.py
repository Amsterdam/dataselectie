import time

from jwcrypto.jwt import JWT
from authorization_django.jwks import get_keyset
import authorization_levels

AUTH_HEADER = 'HTTP_AUTHORIZATION'


class AuthorizationSetup(object):
    """
    Helper methods to setup JWT tokens and authorization levels
    """

    def setup_authorization(self):
        """
        SET

        token_default
        token_scope_hr_r
        token_scope_brk_plus
        header_auth_default
        header_auth_scope_hr_r
        header_auth_scope_brk_plus
        """
        jwks = get_keyset()
        assert len(jwks['keys']) > 0

        key = next(iter(jwks['keys']))
        now = int(time.time())

        header = {
            'alg': 'ES256',  # algorithm of the test key
            'kid': key.key_id
        }
        token_default = JWT(
            header=header,
            claims={
                'iat': now, 'exp': now + 600, 'scopes': []
            }
        )
        token_scope_hr_r = JWT(
            header=header,
            claims={
                'iat': now, 'exp': now + 600, 'scopes': [authorization_levels.SCOPE_HR_R]
            }
        )
        token_scope_brk_plus = JWT(
            header=header,
            claims={
                'iat': now, 'exp': now + 600,
                'scopes': [
                    authorization_levels.SCOPE_HR_R,
                    authorization_levels.SCOPE_BRK_RS,
                    authorization_levels.SCOPE_BRK_RSN
                ]
            }
        )
        token_default.make_signed_token(key)
        self.token_default = token_default.serialize()
        self.header_auth_default = {
            AUTH_HEADER: "Bearer {}".format(self.token_default)
        }
        token_scope_hr_r.make_signed_token(key)
        self.token_scope_hr_r = token_scope_hr_r.serialize()
        self.header_auth_scope_hr_r = {
            AUTH_HEADER: "Bearer {}".format(self.token_scope_hr_r)
        }
        token_scope_brk_plus.make_signed_token(key)
        self.token_scope_brk_plus = token_scope_brk_plus.serialize()
        self.header_auth_scope_brk_plus = {
            AUTH_HEADER: "Bearer {}".format(self.token_scope_brk_plus)
        }
