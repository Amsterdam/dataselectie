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


def meta_q(query, add_aggs=False, sort=True):
    if add_aggs:
        aggs = create_aggs()
    else:
        aggs = None
    sort = {
        'sort': {
            'bezoekadres_openbare_ruimte': { "order": "asc" },
            'bezoekadres_huisnummer': { "order": "asc" },
            'bezoekadres_huisletter': { "order": "asc" },
            'bezoekadres_huisnummertoevoeging': { "order": "asc" }
        }
    }
    return create_query(query, aggs, sort, qtype='vestiging')


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
            'openbare_ruimte': {
                'terms': {
                    'field': 'bezoekadres_openbare_ruimte',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'postcode': {
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
                    'field': 'bezoekadres_buurtcombinatie_naam',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'buurt_naam': {
                'terms': {
                    'field': 'bezoekadres_buurt_naam',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                },
            },
            'ggw_naam': {
                'terms': {
                    'field': 'bezoekadres_ggw_naam',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
            'stadsdeel_naam': {
                'terms': {
                    'field': 'bezoekadres_stadsdeel_naam',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },
        }
    }

    return aggs
