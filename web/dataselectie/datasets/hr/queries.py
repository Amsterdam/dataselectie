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


def meta_q(query, add_aggs=False, add_count_aggs=True):
    # @TODO change to setting

    aggs = bld_agg()
    return create_query(query, add_aggs, add_count_aggs, aggs, qtype='vestiging')


def bld_agg() -> dict:
    agg_size = settings.AGGS_VALUE_SIZE
    aggs = {
        'aggs': {
            'vestiging': {
                'children': {"type": "vestiging"},
                "aggs": {
                    'hoofdcategorie': {
                        'terms': {
                            'field': 'hoofdcategorie',
                            'size': agg_size,
                            'order': {'_term': 'asc'}
                        }
                    },
                    'subcategorie': {
                        'terms': {
                            'field': 'subcategorie',
                            'size': agg_size,
                            'order': {'_term': 'asc'}
                        }
                    },
                    'sbi_omschrijving': {
                        'terms': {
                            'field': 'sbi_omschrijving',
                            'size': agg_size,
                            'order': {'_term': 'asc'}
                        }
                    }
                }
            }
        }
    }

    aggs['aggs'].update(bag_bld_agg()['aggs'])
    return aggs
