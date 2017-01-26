import time

from django.conf import settings
from django.core.management import BaseCommand

import datasets.hr.batch as hrbatch
from batch import batch


class Command(BaseCommand):
    datasetcommands = {
        'hr': (hrbatch.ImportHr,)
    }

    ordered = ['hr']

    def add_arguments(self, parser):
        parser.add_argument(
            'dataset',
            nargs='*',
            default=self.ordered,
            help="Dataset to use, choose from {}".format(
                ', '.join(self.datasetcommands.keys())))

        parser.add_argument(
            '--partial',
            action='store',
            dest='partial_index',
            default=0,
            help='Build X/Y parts 1/3, 2/3, 3/3')

    def handle(self, *args, **options):

        dataset = options['dataset']

        start = time.time()

        for ds in dataset:
            if ds not in self.ordered:
                self.stderr.write("Unkown dataset: {}".format(ds))
                return

        sets = [ds for ds in self.ordered if ds in dataset]  # enforce order

        self.stdout.write("Working on {}".format(", ".join(sets)))

        set_partial_config(options)

        for ds in sets:
            for job_class in self.datasetcommands[ds]:
                batch.execute(job_class(), )

        self.stdout.write(
            "Total Duration: %.2f seconds" % (time.time() - start))


def set_partial_config(options):
    """
    Do partial configuration
    """
    if options['partial_index']:
        numerator, denominator = options['partial_index'].split('/')

        numerator = int(numerator) - 1
        denominator = int(denominator)

        assert (numerator < denominator)

        settings.PARTIAL_IMPORT['numerator'] = numerator
        settings.PARTIAL_IMPORT['denominator'] = denominator
