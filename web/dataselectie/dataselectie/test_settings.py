from .settings import *

TEST_RUNNER = 'dataselectie.utils.ManagedModelTestRunner'

# Setting test prefix on index names in test
if IN_TEST_MODE:
    MIN_BAG_NR = 0
    MIN_HR_NR = 0
    for k, v in ELASTIC_INDICES.items():
        ELASTIC_INDICES[k] = 'test_{}'.format(v)

DATAPUNT_AUTHZ = {
    'JWT_SECRET_KEY': 'TEST_SECRET_KEY_ENZO_SDFKJHSDFLKSJDHFSDKJFHSDLKJFHLSDJSKHJ',
    'JWT_ALGORITHM': 'HS256'
}
