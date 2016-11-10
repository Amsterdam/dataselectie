# Packages
from django.apps import apps
from django.test.runner import DiscoverRunner


# class ManagedModelTestRunner(DiscoverRunner):
#     """
#     Test runner that automatically makes all unmanaged models in your Django
#     project managed for the duration of the test run, so that one doesn't need
#     to execute the SQL manually to create them.
#     """
#     def __init__(self, *args, **kwargs):
#         super(ManagedModelTestRunner, self).__init__(*args, **kwargs)
#         self.verbosity = 2
#
#     def setup_test_environment(self, *args, **kwargs):
#         print(apps)
#         print(apps.all_models)
#         self.unmanaged_models = [model for _, model in apps.all_models['bag', 'hr'].items() if not model._meta.managed]
#         for m in self.unmanaged_models:
#             m._meta.managed = True
#         super(ManagedModelTestRunner, self).setup_test_environment(**kwargs)
#
#     def teardown_test_environment(self, *args, **kwargs):
#         super(ManagedModelTestRunner, self).teardown_test_environment(**kwargs)
#         # reset unmanaged models
#         for m in self.unmanaged_models:
#             m._meta.managed = False
