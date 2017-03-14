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


def create_query(query, aggs=None, sort=None, default_query=None, qtype=None):
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

    if aggs:
        q.update(aggs)
    if sort:
        q.update(sort)
    return q
