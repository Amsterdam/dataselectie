# Tests

from zelfbediening.settings import *

DEBUG = True

DATABASE_ROUTERS = []

TEST_RUNNER = 'zelfbediening.utils.ManagedModelTestRunner'
IN_TEST_MODE = True
