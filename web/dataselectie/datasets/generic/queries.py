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

import logging

log = logging.getLogger(__name__)


def add_aggregations(aggs):
    count_aggs = {}
    # Creating count aggs per aggregatie settings.AGGS_VALUE_SIZE
    for key, value in aggs.items():
        if 'terms' in aggs[key]:
            count_aggs[key + '_count'] = {
                'cardinality': {
                    'field': aggs[key]['terms']['field'],
                    'precision_threshold': 1000
                }
            }
    aggs.update(count_aggs)
    return aggs


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
            'query': {"bool": {"must": [{'term': {'_type': qtype}}]}}
        }
    else:
        q = {
            'query': {'match_all': {}}
        }

    if add_aggs:
        q.update(aggs)
        if add_count_aggs:
            q['aggs'].update(add_aggregations(aggs['aggs']))

    return q
