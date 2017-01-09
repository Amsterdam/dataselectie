from django.core.management import BaseCommand

from django.conf import settings

import datasets.generic.batch as genbatch
import datasets.bag.batch as bagbatch
import datasets.hr.batch as hrbatch
from batch import batch
import time


class Command(BaseCommand):

    ordered = ['ds_bag']

    indexes = {
        'ds_bag': [bagbatch.BuildIndexDsBagJob, hrbatch.BuildIndexHrJob]
    }

    hrindexes = {
        'ds_bag': [hrbatch.BuildIndexHrJob]
    }

    bagindexes = {
        'ds_bag': [hrbatch.BuildIndexHrJob]
    }

    recreate_indexes = {
        'ds_bag': [genbatch.ReBuildIndexDsJob]
    }

    def add_arguments(self, parser):
        parser.add_argument(
            'dataset',
            nargs='*',
            default=self.ordered,
            help="Dataset to use, choose from {}".format(
                ', '.join(self.indexes.keys())))

        parser.add_argument(
            '--build',
            action='store_true',
            dest='build_all_indexes',
            default=False,
            help='Build all elastic indexes from postgres')

        parser.add_argument(
            '--buildhr',
            action='store_true',
            dest='build_hrindex',
            default=False,
            help='Build hr-index from postgres')

        parser.add_argument(
            '--buildbag',
            action='store_true',
            dest='build_bagindex',
            default=False,
            help='Build bag-index from postgres')

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
            if ds not in self.indexes.keys():
                self.stderr.write("Unkown dataset: {}".format(ds))
                return

        sets = [ds for ds in self.ordered if ds in dataset]     # enforce order

        self.stdout.write("Working on {}".format(", ".join(sets)))

        self.set_partial_config(sets, options)

        for ds in sets:
            if options['recreate_indexes']:
                for job_class in self.recreate_indexes[ds]:
                    batch.execute(job_class())
                # we do not run the other tasks
                continue  # to next dataset please..

            if options['build_all_indexes']:
                for job_class in self.indexes[ds]:
                    batch.execute(job_class(), )

            if options['build_hrindex']:
                for job_class in self.hrindexes[ds]:
                    batch.execute(job_class(), )

            if options['build_bagindex']:
                for job_class in self.bagindexes[ds]:
                    batch.execute(job_class(), )

        self.stdout.write(
            "Total Duration: %.2f seconds" % (time.time() - start))
