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
    sort = {
        'sort': {
            'openbare_ruimte_naam': {"order": "asc"},
            'huisnummer': {"order": "asc"},
            'huisletter': {"order": "asc"},
            'huisnummer_toevoeging': {"order": "asc"}
        }
    }
    return create_query(query, aggs, sort, qtype='eigendom')


def create_aggs():
    agg_size = settings.AGGS_VALUE_SIZE
    aggs = {
        'aggs': {
            'eigenaar_cat': {
                'terms': {
                    'field': 'eigenaar_cat',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'grondeigenaar': {
                'terms': {
                    'field': 'grondeigenaar',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'aanschrijfbaar': {
                'terms': {
                    'field': 'aanschrijfbaar',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'appartementeigenaar': {
                'terms': {
                    'field': 'appartementeigenaar',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'postcode': {
                'terms': {
                    'field': 'postcode',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'openbare_ruimte_naam': {
                'terms': {
                    'field': 'openbare_ruimte_naam',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'wijk_naam': {
                'terms': {
                    'field': 'wijk_naam',
                    'size': agg_size,
                     'order': {'_term': 'asc'},
                },
            },
            'wijk_code': {
                'terms': {
                    'field': 'wijk_code',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'buurt_code': {
                'terms': {
                    'field': 'buurt_code',
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
            'ggw_code': {
                'terms': {
                    'field': 'ggw_code',
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
            'stadsdeel_code': {
                'terms': {
                    'field': 'stadsdeel_code',
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
