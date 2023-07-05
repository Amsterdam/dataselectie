import logging
from django.core.management import BaseCommand

from django.db import connection
from psycopg2.sql import SQL, Identifier

bag_tables = (
	"bag_bouwblok",
	"bag_bron",
	"bag_buurt",
	"bag_buurtcombinatie",
	"bag_gebiedsgerichtwerken",
	"bag_gemeente",
	"bag_grootstedelijkgebied",
	"bag_ligplaats",
	"bag_nummeraanduiding",
	"bag_openbareruimte",
	"bag_pand",
	"bag_stadsdeel",
	"bag_standplaats",
	"bag_unesco",
	"bag_verblijfsobject",
	"bag_verblijfsobjectpandrelatie",
	"bag_woonplaats",
	"brk_aardzakelijkrecht",
	"brk_adres",
	"brk_cultuurcodebebouwd",
	"brk_cultuurcodeonbebouwd",
	"brk_eigendom",
	"brk_eigenaar",
	"brk_eigenaarcategorie",
	"brk_erfpacht",
	"brk_gemeente",
	"brk_geslacht",
	"brk_kadastraalobject",
	"brk_kadastraalobjectverblijfsobjectrelatie",
	"brk_kadastralegemeente",
	"brk_kadastralesectie",
	"brk_land",
	"brk_rechtsvorm",
	"brk_zakelijkrecht",
	"brk_zakelijkrechtverblijfsobjectrelatie",
)


def build_dataselectie_database(
    bag_schema, handelsregister_schema, dataselectie_schema
):
    with connection.cursor() as cursor:
        for table in bag_tables:
            logging.info("Creating table %s", table)
            cursor.execute(
                SQL("DROP TABLE IF EXISTS {}").format(
                    Identifier(dataselectie_schema, table),
                )
            )
            cursor.execute(
                SQL("CREATE TABLE {} AS SELECT * FROM {}").format(
                    Identifier(dataselectie_schema, table),
                    Identifier(bag_schema, table),
                )
            )

        logging.info("Creating table hr_dataselectie")
        cursor.execute(
            SQL("CREATE TABLE {} AS SELECT * FROM {}").format(
                Identifier(dataselectie_schema, "hr_dataselectie"),
                Identifier(handelsregister_schema, "hr_dataselectie"),
            )
        )


def build_bag_indexes_sql():
    with connection.cursor() as cursor:
        sql = open("datasets/bag/migrations/bag_sql_indexes.sql").read()
        cursor.execute(sql)


def build_bag_contraints_sql():
    with connection.cursor() as cursor:
        sql = open("datasets/bag/migrations/bag_sql_constraints.sql").read()
        cursor.execute(sql)


class Command(BaseCommand):
    help = """
    This script prepares the "dataselectie" database by copying
    tables from the "bag" and "handelsregister" schemas.
    The output is then be used as input to the Elasticsearch indexing
    command (the management command 'elastic_indices').

    This process consists of the following optional steps:

    1) copy the tables defined below from the 'bag-schema' to the 'dataselectie-schema'
    2) copy the hr_dataselectie table from the 'hr-schema' to the 'dataselectie-schema'
    3) apply indexes and constraints to the copied tables (the 'import' management command).

    On Azure, the dataselectie "database" is a separate schema with data loaded from other
    legacy-schemas. We use the build-db option to fill this schema.

    On CloudVPS, the logic from the 'build-db' step is executed on Jenkins through separate
    shell scripts in this repository.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--build-db",
            nargs=3,
            help="""
            If provided, build the database using the given three schemas. 
            The order of args have the following meaning:
            --build-db <bag-schema> <hr-schema> <dataselectie-schema>
            """,
        )
        parser.add_argument(
            "--bagdbindexes",
            action="store_true",
            dest="dbindex",
            default=False,
            help="Apply indexes to the tables imported from the bag_v11 database",
        )

        parser.add_argument(
            "--bagdbconstraints",
            action="store_true",
            dest="constraints",
            default=False,
            help="Apply constraints to the tables imported from the bag_v11 database",
        )

    def handle(self, *args, **options):
        if options["build_db"]:
            build_dataselectie_database(*options["build_db"])

        if options["dbindex"]:
            build_bag_indexes_sql()

        if options["constraints"]:
            build_bag_contraints_sql()
