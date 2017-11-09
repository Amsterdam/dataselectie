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
            'handelsnaam': {"order": "asc"},
            'bezoekadres_openbare_ruimte': {"order": "asc"},
            'bezoekadres_huisnummer': {"order": "asc"},
            'bezoekadres_huisletter': {"order": "asc"},
            'bezoekadres_huisnummertoevoeging': {"order": "asc"}
        }
    }
    return create_query(query, aggs, sort, qtype='vestiging')


def create_aggs() -> dict:
    agg_size = settings.AGGS_VALUE_SIZE
    aggs = {
        'aggs': {
            'hoofdcategorie': {
                'terms': {
                    'field': 'hoofdcategorie',
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
            'bijzondere_rechtstoestand': {
                'terms': {
                    'field': 'bijzondere_rechtstoestand',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },

            # A tm Z listing we do not use (yet)
            #  'sbi_l1': {
            #    'terms': {
            #        'field': 'sbi_l1',
            #        'size': agg_size,
            #        'order': {'_term': 'asc'},
            #    }
            # },

            'sbi_l2': {
                'terms': {
                    'field': 'sbi_l2',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },

            'sbi_l3': {
                'terms': {
                    'field': 'sbi_l3',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },

            'sbi_l4': {
                'terms': {
                    'field': 'sbi_l4',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },

            'sbi_l5': {
                'terms': {
                    'field': 'sbi_l5',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            },

            'sbi_code': {
                'terms': {
                    'field': 'sbi_code',
                    'size': agg_size,
                    'order': {'_term': 'asc'},
                }
            }
        }
    }

    count_aggs = {}

    for key, aggregatie in aggs['aggs'].items():
        count_aggs[f'{key}_count'] = {
            'cardinality': {
                'field': aggregatie['terms']['field'],
                'precision_threshold': 1000
            }
        }

    aggs['aggs'].update(count_aggs)

    return aggs
