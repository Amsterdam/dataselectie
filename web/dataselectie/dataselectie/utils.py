# Packages
from django.apps import apps
from django.test.runner import DiscoverRunner


class ManagedModelTestRunner(DiscoverRunner):
    """
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run, so that one doesn't need
    to execute the SQL manually to create them.
    """
    def __init__(self, *args, **kwargs):
        super(ManagedModelTestRunner, self).__init__(*args, **kwargs)
        self.verbosity = 2
        self.unmanaged_models = []

    def setup_test_environment(self, *args, **kwargs):
        datasets = ['bag', 'hr']  # update when new datasets are introdiced
        for dataset in datasets:
            self.unmanaged_models.extend(
                [model for _, model in apps.all_models[dataset].items() if not model._meta.managed]
            )
        for m in self.unmanaged_models:
            m._meta.managed = True
        super(ManagedModelTestRunner, self).setup_test_environment(**kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(ManagedModelTestRunner, self).teardown_test_environment(**kwargs)
        # reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False
