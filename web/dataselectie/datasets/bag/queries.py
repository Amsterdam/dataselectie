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


def meta_q(query, add_aggs=True, add_count_aggs=True):
    # @TODO change to setting
    agg_size = settings.AGGS_VALUE_SIZE
    aggs = {
        'aggs': {
            'postcode': {
                'terms': {
                    'field': 'postcode',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'naam': {
                'terms': {
                    'field': 'naam',
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
            'buurtcombinatie_code': {
                'terms': {
                    'field': 'buurtcombinatie_code',
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

    if query:
        q = {
            'query': {'match': {'_all': query}},
        }
    else:
        q = {
            'query': {'match_all': {}}
        }

    if add_aggs:
        if add_count_aggs:
            count_aggs = {}
            # Creating count aggs per aggregatie settings.AGGS_VALUE_SIZE
            for key, value in aggs['aggs'].items():
                count_aggs[key + '_count'] = {
                    'cardinality': {
                        'field': aggs['aggs'][key]['terms']['field'],
                        'precision_threshold': 1000
                    }
                }
            aggs['aggs'].update(count_aggs)
        q.update(aggs)
    return q
