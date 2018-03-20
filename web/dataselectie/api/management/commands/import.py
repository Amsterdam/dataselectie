from django.core.management import BaseCommand

from django.db import connection


def build_bag_indexes_sql():
    with connection.cursor() as cursor:
        sql = open('datasets/bag/migrations/bag_sql_indexes.sql').read()
        cursor.execute(sql)


def build_bag_contraints_sql():
    with connection.cursor() as cursor:
        sql = open('datasets/bag/migrations/bag_sql_constraints.sql').read()
        cursor.execute(sql)


class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            '--bagdbindexes',
            action='store_true',
            dest='dbindex',
            default=False,
            help='Build all elastic indexes from postgres')

        parser.add_argument(
            '--bagdbconstraints',
            action='store_true',
            dest='constraints',
            default=False,
            help='Delete and recreate elastic indexes')

    def handle(self, *args, **options):

        if options['dbindex']:
            build_bag_indexes_sql()

        if options['constraints']:
            build_bag_contraints_sql()
