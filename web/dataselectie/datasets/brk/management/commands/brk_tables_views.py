import logging
from django.core.management import BaseCommand
from django.db import connection
from datasets import validate_tables
from datasets.brk.management import brk_batch_sql

log = logging.getLogger(__name__)



class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            '--validate',
            action='store_true',
            dest='validate',
            default=False,
            help='Validate table count')

    def handle(self, *args, **options):

        with connection.cursor() as c:
            for sql_command in brk_batch_sql.bagimport_sql_commands \
                               + brk_batch_sql.dataselection_sql_commands\
                               + brk_batch_sql.mapselection_sql_commands:
                info = (sql_command[:64] + '..') if len(sql_command) > 64 else sql_command
                log.info(f"Execute SQL: {info}")
                c.execute(sql_command)

        if options['validate']:
            log.info("Validating tables")
            validate_tables.check_table_targets()
            return
