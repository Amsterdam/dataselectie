#!/usr/bin/env python
import os
import sys
import time
from authorization_django import jwks
import jwt


def make_superemployee_token():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    lib_dir = os.path.abspath(os.path.join(script_dir, os.path.pardir, os.path.pardir))
    sys.path.append(lib_dir)
    from dataselectie.settings import DATAPUNT_AUTHZ

    jwks_string = DATAPUNT_AUTHZ['JWKS']
    jwks_signers = jwks.load(jwks_string).signers

    assert len(jwks_signers) > 0
    if len(jwks_signers) == 0:
        print("""

                WARNING WARNING WARNING

                'JWT_SECRET_KEY' MISSING!!

                """)
        return False

    list_signers = [(k, v) for k, v in jwks_signers.items()]
    (kid, key) = list_signers[len(list_signers) - 1]

    now = int(time.time())

    token_scope_grex_r = jwt.encode({
        'scopes': ['HR/R', 'BRK/RSN', 'BRK/RSN'],
        'iat': now, 'exp': now + 600}, key.key, algorithm=key.alg,
        headers={'kid': kid})

    return str(token_scope_grex_r, 'utf-8')


if __name__ == "__main__":
    print(make_superemployee_token())
