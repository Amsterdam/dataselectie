"""
==================================================
 Individual search queries for external systems
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""
# Python
# Packages
# from elasticsearch_dsl import Search, Q, A

from elasticsearch_dsl import Q

import logging

log = logging.getLogger(__name__)


def create_query(query, add_aggs, add_count_aggs, aggs, default_query=None, qtype=None):

    if default_query:
        if query:
            query += default_query
        else:
            query = default_query

    if query:
        q = {
            'query': {'match': {'_all': query}},
        }
    elif qtype:
        q = {
            'query': {"bool": {"should": [{'term': {'_type': qtype}}]}}
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
