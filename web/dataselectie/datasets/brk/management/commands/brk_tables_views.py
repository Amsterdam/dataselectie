from django.core.management import BaseCommand
from django.db import connection
from . import brk_batch_sql


class Command(BaseCommand):

    def handle(self, *args, **options):

        with connection.cursor() as c:

            for sql_command in brk_batch_sql.dataselection_sql_commands:
                c.execute(sql_command)

            for sql_command in brk_batch_sql.carto_sql_commands:
                c.execute(sql_command)
