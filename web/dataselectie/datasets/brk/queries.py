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
from ..generic.queries import create_query


def meta_q(query: str, add_aggs=True, sort=True) -> dict:
    # @TODO change to setting
    if add_aggs:
        aggs = create_aggs()
    else:
        aggs = None
    sort_values = {
        'sort': {
            'aanduiding': {"order": "asc"},
            'aard_zakelijk_recht': {"order": "asc"},
            'zakelijk_recht_aandeel_float': {"order": "desc"},
            'sjt_geslachtsnaam': {"order":"asc"}
        }
    } if sort else None
    return create_query(query, aggs, sort_values, qtype='eigendom')


def create_aggs():
    agg_size = settings.AGGS_VALUE_SIZE
    aggs = {
        'aggs': {
            'eigenaar_type': {
                'terms': {
                    'field': 'eigenaar_type',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'eigenaar_cat': {
                'terms': {
                    'field': 'eigenaar_cat',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'buurtcombinatie_naam': {
                'terms': {
                    'field': 'buurtcombinatie_naam',
                    'size': agg_size,
                     'order': {'_term': 'asc'},
                },
            },
            'buurt_naam': {
                'terms': {
                    'field': 'buurt_naam',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'ggw_naam': {
                'terms': {
                    'field': 'ggw_naam',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'stadsdeel_naam': {
                'terms': {
                    'field': 'stadsdeel_naam',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
        }
    }
    # Adding count aggregations
    count_aggs = {}
    for key, aggregatie in aggs['aggs'].items():
        count_aggs[f'{key}_count'] = {
            'cardinality' : {
                'field' : aggregatie['terms']['field'],
                'precision_threshold': 1000
            }
        }
    aggs['aggs'].update(count_aggs)
    return aggs
