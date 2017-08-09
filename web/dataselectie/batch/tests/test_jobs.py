from django.test import TestCase, SimpleTestCase
from django.utils import timezone

import batch.batch as batch


class EmptyJob(object):
    name = "empty"

    def tasks(self):
        return []


class FailingTask(object):
    name = "failing"

    def execute(self):
        raise Exception("Oops")


class FailedJob(object):
    name = "failed"

    def tasks(self):
        return [FailingTask()]


class SimpleJob(object):
    def __init__(self, name, *tasks):
        self.name = name
        self._tasks = tasks

    def tasks(self):
        return self._tasks


class JobTest(TestCase):

    def test_job_results_in_execution(self):
        batch.execute(EmptyJob())
