# Python
import copy
import logging
# Packages
import rapidjson
# Project

log = logging.getLogger(__name__)


class BadReq(Exception):
    pass


class ElasticSearchMixin(object):
    """
    A mixin provinding several elastic search utility functions

    geo_fields tuple format per dict is as follow:
        - key: the field to use,
        - value: type of geospatial search

    """

    # A set of optional keywords to filter the results further
    keywords = ()
    geo_fields = {
        'shape': ['centroid', 'geo_polygon'],
    }
    raw_fields = []
    keyword_mapping = {}
    default_search = 'term'
    request = None

    def build_elastic_query(self, query):
        """
        Builds the dictionary query to send to elastic
        Parameters:
        query - The q dict returned from the queries file
        Returns:
        The following query dict is sent to elastic
        from dataselectie-hr and will return the
        vestigingsinfo and the bag info,
        The matchall will make sure that the
        linked info from bag is retrieved

        {
            "query":{
                "bool": {
                    "must": [
                        {
                            "term": {"_type": "bag_locatie"}
                        },{
                            "has_child": {
                                "type": "vestiging",
                                "query": [
                                    {
                                        "term": {"sbi_code": "6420"}
                                    }
                                ],
                                "inner_hits":{}
                            }
                        }
                    ]
                }
            },
             "aggs": {
                  "nummeraanduiding": {
                     "terms": {
                        "field": "_type"
                     },
                     "aggs": {
                        "vestiging": {
                           "children": {
                              "type": "vestiging"
                           },
                           "aggs": {
                              "bedrijf": {
                                 "term": {
                                    "field": "bedrijfsnaam"
                                 }
                              }
                           }
                        }
                     }
                  }
              }
          }
        The "match_all" can be replaced with selections on the
        parent. i.e. buurtnaam:
        {
            "bool": {
                "must: [
                    { "match": {"stadsdeel_naam": "Centrum"}}
                ]
            }
        }
        """
        # Adding filters
        filters = []
        # Retrieving the request parameters
        request_parameters = getattr(self.request, self.request.method)

        self.selection = []         # cash bashing!
        # Checking for known keyword filters
        for filter_keyword in self.keywords:
            val = request_parameters.get(filter_keyword, None)
            # Since a parameter can be 0, which evalutes to False, a check
            # is actually made that the value is not None
            if val is not None:     # parameter is entered
                filters.append({self.default_search: self.get_term_and_value(filter_keyword, val)})
                self.filterkeys(filter_keyword, val)

        # Adding geo filters
        for term, geo_type in self.geo_fields.items():
            val = request_parameters.get(term, None)
            if val is not None:
                # Checking if val needs to be converted from string
                if isinstance(val, str):
                    try:
                        val = rapidjson.loads(val)
                    except ValueError:
                        # Bad formatted json.
                        val = []
                # Only adding filter if at least 3 points are given
                if (len(val)) > 2:
                    filters.append({geo_type[1]: {geo_type[0]: {'points': val}}})

        query = {
            'query': {
                'bool': {
                    'must': [query['query']],
                    'filter': filters,
                }
            }
        }

        return self.handle_query_size_offset(query)

    def filterkeys(self, filter_keyword: str, val: str):
        pass

    def proc_parameters(self, filter_keyword: str, val: str, filters: list) -> (list, list):
        filters.append({self.default_search: self.get_term_and_value(filter_keyword, val)})
        return filters

    def handle_query_size_offset(self, query: dict) -> dict:
        """
        Handles query size and offseting
        By defualt it does nothing
        """
        return query

    def get_term_and_value(self, filter_keyword: str, val: str) -> dict:
        """
        Some fields need to be searched raw while others are analysed with the default string analyser which will
        automatically convert the fields to lowercase in de the index.
        :param filter_keyword: the keyword in the index to search on
        :param val: the value we are searching for
        :return: a small dict that contains the key/value pair to use in the ES search.
        """
        if filter_keyword in self.raw_fields:
            filter_keyword = "{}.raw".format(filter_keyword)
        return {filter_keyword: val}
