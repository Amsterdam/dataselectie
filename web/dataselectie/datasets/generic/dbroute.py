from django.conf import settings


class DatasetsRouter(object):
    """
    Routes Datasets to their applicable databases
    For this to work the name of the database settings and the name
    of the dataset application need to match.

    example: bag dataset with BAG database settings
    """

    datasets = ('bag', 'hr')  # A list of available datasets

    def _model_in_datasets(self, app):
        """
        Checks that the app the model belongs to is
        a dataset app
        """
        return app in self.datasets

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if self._model_in_datasets(model._meta.app_label):
            return model._meta.app_label
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if self._model_in_datasets(model._meta.app_label):
            # Only allow writing in testing
            if settings.IN_TEST_MODE:
                return model._meta.app_label
            return False
        # Not a dataset app.
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Do Not allowe migration of datasets. This should already be handled by
        managed=False, but jsut to be sure
        """
        if self._model_in_datasets(app_label) and not settings.IN_TEST_MODE:
            return False
        elif self._model_in_datasets(app_label) and db != app_label:
            return False
        return None
