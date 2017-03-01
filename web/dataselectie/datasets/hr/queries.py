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


def meta_q(query, add_aggs=False, add_count_aggs=True):
    # @TODO change to setting
    print('Loading query')
    aggs = create_aggs()
    return create_query(query, add_aggs, add_count_aggs, aggs, qtype='vestiging')


def create_aggs() -> dict:
    agg_size = settings.AGGS_VALUE_SIZE
    aggs = {
        'aggs': {
            'hcat': {
                'terms': {
                    'field': 'hcat',
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
            'scat': {
                'terms': {
                    'field': 'scat',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'subcategorie': {
                'terms': {
                    'field': 'subcategorie',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'bezoekadres_openbare_ruimte': {
                'terms': {
                    'field': 'bezoekadres_openbare_ruimte',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'bezoekadres_postcode': {
                'terms': {
                    'field': 'bezoekadres_postcode',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'kvk_nummer': {
                'terms': {
                    'field': 'kvk_nummer',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
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

    return aggs
