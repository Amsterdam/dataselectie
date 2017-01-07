from abc import ABCMeta, abstractmethod
import logging
import sys

from django.utils import timezone
import gc

from batch.models import JobExecution, TaskExecution

log = logging.getLogger(__name__)


def execute(job):
    log.info("Starting job: %s", job.name)

    job_execution = JobExecution.objects.create(name=job.name)

    try:
        for t in job.tasks():
            _execute_task(job_execution, t)
    except:
        log.exception("Job failed: %s", job.name)
        sys.exit(1)

    log.info("Finished job: %s", job.name)
    job_execution.date_finished = timezone.now()
    job_execution.status = JobExecution.STATUS_FINISHED
    job_execution.save()

    return job_execution


def _execute_task(job_execution, task):
    if callable(task):
        task_name = task.__name__
        execute_func = task
        # tear_down = None
    else:
        task_name = getattr(task, "name", "no name specified")
        execute_func = task.execute
        # tear_down = getattr(task, "tear_down", None)

    log.debug("Starting task: %s", task_name)
    task_execution = TaskExecution.objects.create(
        job=job_execution, name=task_name, date_started=timezone.now()
    )

    try:
        execute_func()
    except:
        log.exception("Task failed: %s", task_name)
        sys.exit(1)

    log.debug("Finished task: %s", task_name)
    task_execution.date_finished = timezone.now()
    task_execution.status = TaskExecution.STATUS_FINISHED
    task_execution.save()


class BasicTask(object):
    """
    Abstract task that splits execution into three parts:

    * ``before``
    * ``process``
    * ``after``

    ``after`` is *always* called, whether ``process`` fails or not
    """

    class Meta:
        __class__ = ABCMeta

    def execute(self):
        try:
            self.before()
            self.process()
        finally:
            self.after()
            gc.collect()

    @abstractmethod
    def before(self):
        pass

    @abstractmethod
    def after(self):
        pass

    @abstractmethod
    def process(self):
        pass


class Statistics:
    def __init__(self):
        self.counters = {}
        self.extra_info = {}
        self.totaal = 0

    def add(self, reporting_group, extra_info=None, total=True):

        if not reporting_group in self.counters:
            self.counters[reporting_group] = 1
        else:
            self.counters[reporting_group] += 1

        if extra_info:
            if reporting_group in self.extra_info:
                self.extra_info[reporting_group].append(extra_info)
            else:
                self.extra_info[reporting_group] = [extra_info]

        if total:
            self.totaal += 1
            
    def report(self):
        for reporting_group, count in self.counters.items():
            print('{0: <50}: {1}'.format(reporting_group, count))
        self.counters = {}
        if self.totaal:
            print('{0: <50}: {1}'.format('* totaal', self.totaal))
            self.totaal = 0
            
    def report_extra_info(self):
        for reporting_group, extra_info in self.extra_info.items():
            print('\n' + reporting_group)
            for e_info in extra_info:
                print(e_info)
        self.extra_info = {}

statistics = Statistics()