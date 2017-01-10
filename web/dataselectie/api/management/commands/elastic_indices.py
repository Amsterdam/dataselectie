from django.core.management import BaseCommand

from django.conf import settings

import datasets.generic.batch as genbatch
import datasets.bag.batch as bagbatch
import datasets.hr.batch as hrbatch
from batch import batch
import time


class Command(BaseCommand):

    indexname = 'ds_bag'
    datasetcommands = {
        'bag': (bagbatch.BuildIndexDsBagJob,),
        'hr': (hrbatch.BuildIndexHrJob,)
    }

    ordered = ['bag', 'hr']

    recreate_indexes = {
        'bag': (genbatch.ReBuildIndexDsJob,)
    }

    def add_arguments(self, parser):
        parser.add_argument(
            'dataset',
            nargs='*',
            default=self.ordered,
            help="Dataset to use, choose from {}".format(
                ', '.join(self.datasetcommands.keys())))

        parser.add_argument(
            '--build',
            action='store_true',
            dest='build',
            default=False,
            help='Build all elastic indexes from postgres')

        parser.add_argument(
            '--recreate',
            action='store_true',
            dest='recreate_indexes',
            default=False,
            help='Delete and recreate elastic indexes')

        parser.add_argument(
            '--partial',
            action='store',
            dest='partial_index',
            default=0,
            help='Build X/Y parts 1/3, 2/3, 3/3')

    def set_partial_config(self, sets, options):
        """
        Do partial configuration
        """
        if options['partial_index']:
            numerator, denominator = options['partial_index'].split('/')

            numerator = int(numerator) - 1
            denominator = int(denominator)

            assert(numerator < denominator)

            settings.PARTIAL_IMPORT['numerator'] = numerator
            settings.PARTIAL_IMPORT['denominator'] = denominator

    def handle(self, *args, **options):

        dataset = options['dataset']

        start = time.time()

        for ds in dataset:
            if ds not in self.ordered:
                self.stderr.write("Unkown dataset: {}".format(ds))
                return

        sets = [ds for ds in self.ordered if ds in dataset]     # enforce order

        self.stdout.write("Working on {}".format(", ".join(sets)))

        self.set_partial_config(sets, options)

        for ds in sets:
            if options['recreate_indexes']:
                if ds in self.recreate_indexes:
                    for job_class in self.recreate_indexes[ds]:
                            batch.execute(job_class())
                # we do not run the other tasks
                continue  # to next dataset please..

            if options['build']:
                for job_class in self.datasetcommands[ds]:
                    batch.execute(job_class(), )

        self.stdout.write(
            "Total Duration: %.2f seconds" % (time.time() - start))
