"""
==================================================
 Individual search queries
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""

# Packages
from django.conf import settings
from ..bag.queries import bld_agg as bag_bld_agg
from ..generic.queries import create_query

def meta_q(query, add_aggs=True, add_count_aggs=True):
    # @TODO change to setting

    aggs = bld_agg()
    return create_query(query, add_aggs, add_count_aggs, aggs)


def bld_agg() -> dict:
    agg_size = settings.AGGS_VALUE_SIZE
    aggs = {
        'aggs': {
            'sbi_code': {
                'terms': {
                    'field': 'sbi_code',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'subcategorie': {
                'terms': {
                    'field': 'subcategorie',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'sub_sub_categorie': {
                'terms': {
                    'field': 'sub_sub_categorie',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'hoofdcategorie': {
                'terms': {
                    'field': 'hoofdcategorie',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
        }
    }

    aggs.update(bag_bld_agg())
    return aggs