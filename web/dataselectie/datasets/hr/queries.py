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
    aggs = {"aggs": {
                "sbi_codes": {
                    "nested": {
                        "path": "sbi_codes"
                    },
                    "aggs": {
                        "sbi_code_count": {
                            "terms": {
                                "field": "sbi_codes.sbi_code",
                                "size": agg_size,
                                "order": {"_term": "asc"}
                            }
                        },
                        "subcategorie_count": {
                            "terms": {
                                "field": "sbi_codes.subcategorie",
                                "size": agg_size,
                                "order": {"_term": "asc"}
                            }
                        },
                        "sub_sub_categorie_count": {
                            "terms": {
                                "field": "sbi_codes.sub_sub_categorie",
                                "size": agg_size,
                                "order": {"_term": "asc"}
                            }
                        },
                        "hoofdcategorie_count": {
                            "terms": {
                                "field": "sbi_codes.hoofdcategorie",
                                "size": agg_size,
                                "order": {"_term": "asc"}
                            }
                        }
                    }
                }
            }
        }

    aggs['aggs'].update(bag_bld_agg()['aggs'])
    return aggs