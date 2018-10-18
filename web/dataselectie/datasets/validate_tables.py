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
    check if current table counts are close
    """
    error = False
    all_msg = ("Table count errors \n"
               "Count,    Target,    Table,           Status \n")

    for target, deviation, table in table_data:
        count = sql_count(table)
        if abs(count - target) > deviation or count == 0:
            status = '<FAIL>'
            error = True
        else:
            status = '< OK >'

        msg = f"{count:>6} ~= {target:<6} {table:<42} {status} \n"
        all_msg += msg

    if error:
        LOG.error(msg)
#        For now only report error
#        raise ValueError(all_msg)
    else:
        LOG.debug(all_msg)


def check_table_targets():
    """
    Check if tables have a specific count
    """
    LOG.debug('Validating table counts..')

    # Count  table
    tables_targets = [
        # counts from 8-10-2018
        # counts, allowed deviation, table
        (384106 ,  38000, "geo_brk_kot_point_in_poly"),
        (543922 ,  54000, "geo_brk_eigendommen"),
        (59441  ,  5900,  "geo_brk_niet_eigendom_poly"),
        (295470 ,  29000, "geo_brk_eigendom_poly"),
        (39774  ,  3900,  "geo_brk_eigendom_point"),
        (24372  ,  2400,  "geo_brk_eigendom_poly_all"),
        (660715 ,  66000, "geo_brk_eigendomselectie"),
        (1407   ,  140,   "geo_brk_rond_erfpacht_poly"),
        (76118  ,  7600,  "geo_brk_erfpacht_poly"),
        (1474   ,  140,   "geo_brk_erfpacht_point"),
        (10140  ,  1000,  "geo_brk_erfpacht_poly_all"),
        (899    ,  90,    "geo_brk_rond_erfpacht_poly_all"),
    ]
    check_table_counts(tables_targets)
