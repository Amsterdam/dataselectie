import logging
from django.core.management import BaseCommand
from django.db import connection
from datasets.brk.management import brk_batch_sql

log = logging.getLogger(__name__)



class Command(BaseCommand):

    def handle(self, *args, **options):

        with connection.cursor() as c:
            for sql_command in brk_batch_sql.bagimport_sql_commands \
                               + brk_batch_sql.dataselection_sql_commands\
                               + brk_batch_sql.mapselection_sql_commands:
                info = (sql_command[:64] + '..') if len(sql_command) > 64 else sql_command
                log.info(f"Execute SQL: {info}")
                c.execute(sql_command)
