"""
collect and validate bag, brk, gebieden and wkpb table counts
"""
import logging
from django.db import connection


LOG = logging.getLogger(__name__)


def sql_count(table):

    count = 0

    with connection.cursor() as c:
        c.execute('SELECT COUNT(*) FROM {}'.format(connection.ops.quote_name(table)))
        row = c.fetchone()
        count += row[0]
        # LOG.debug('COUNT %-6s %s', count, table)

    return count


def check_table_counts(table_data: list):
    """
    Given list with tuples of count - table name
    check if current table counts are not more then 50% off
    """
    error = False
    all_msg = ("Table count errors \n"
               "Count,    Target,    Table,           Status \n")

    for target, table in table_data:
        count = sql_count(table)
        allowed_deviation = target / 2
        if abs(count - target) > allowed_deviation or count == 0:
            status = '<FAIL>'
            error = True
        else:
            status = '< OK >'

        msg = f"{count:>6} ~= {target:<6} {table:<42} {status} \n"
        all_msg += msg

    if error:
        LOG.error(msg)
        raise ValueError(all_msg)
    else:
        LOG.debug(all_msg)


def check_table_targets():
    """
    Check if tables have a specific count
    """
    LOG.debug('Validating table counts..')

    # Count  table
    tables_targets = [
        # counts from 30-10-2018
        # counts, table
        (384550 ,  "geo_brk_kot_point_in_poly"),
        (680658 ,  "geo_brk_eigendommen"),
        (62609  ,  "geo_brk_niet_eigendom_poly"),
        (295655 ,  "geo_brk_eigendom_poly"),
        (41957  ,  "geo_brk_eigendom_point"),
        (24351  ,  "geo_brk_eigendom_poly_all"),
        (847962 ,  "geo_brk_eigendomselectie"),
        (1414   ,  "geo_brk_rond_erfpacht_poly"),
        (76145  ,  "geo_brk_erfpacht_poly"),
        (1479   ,  "geo_brk_erfpacht_point"),
        (10136  ,  "geo_brk_erfpacht_poly_all"),
        (900    ,  "geo_brk_rond_erfpacht_poly_all"),
    ]
    check_table_counts(tables_targets)
