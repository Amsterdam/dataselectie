# Packages
from django.views.generic import ListView
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

# Project
from zelfbediening.datasets.bag import models


class TableSearchView(ListView):
    """
    A base class to generate tables from search results
    """

    # Required attributes:
    #---------------------
    model = None  # The model class to use
    index = ''  # The name of the index to search in
    db = None  # The DB to use for the query This allws usage of different dbs

    # ListView inherintance functions
    def get_queryset(self):
        """
        This function is called by list view to generate the query set
        It is overwritten to first use elastic to retrieve the ids then
        return a queryset based on the ids
        """
        # Loading data from elastic. See function for details
        self.load_from_elastic()
        # Creating a queryset
        qs = self.create_queryset()
        return qs

    def query_elastic(self, query):
        """
        Perform the query to elastic
        """
        elastic = Elasticsearch()
        s = Search().using(client).query(query)

        return s.execute()

    # Functions to implement by subclass
    def load_from_elastic(self):
        """
        Loads the data from elastic.
        It extracts the query parameters from the url and creates a
        query for elastic. The query returns a list of ids relevant to
        the search term as well as a list of possible filters, based on
        aggregates search results. The results are set in the class

        This function must be overwritten by subclasses as it requires
        """
        raise NotImplementedError

    def create_queryset(self):
        """
        Generates a query set based on the ids retrieved from elastic
        """
        raise NotImplementedError
        ids = self.elastic.get('ids', None)
        if ids:
            return self.model.objects.filter(id__in=ids)
        else:
            # No ids where found
            return self.model.objects.none()


class BagSearch(ListView):

    model = models.NummeraanduiduingMeta
    index = 'ZB_BAG'

    def load_from_elastic(self):
        """
        This is the first part of where the magic happens.
        Using the keywords in the get parameter to form a query
        for elastic to retrieve ids and filters.
        possible keywords:

        search - the actual search term
        possbile values:
        """
        # Looking for keywords
        search_term = self.request.GET.get(search_term, None)
        if search_term:
            print('Search term:', search_term)
        #else:
        self.elastic = {
            'ids': None,
            'filters': [],
        }

class NummeraanduidingViewSet(rest.AtlasViewSet):
    """
    Nummeraanduiding

    Een nummeraanduiding, in de volksmond ook wel adres genoemd,
    is een door het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject,
    standplaats of ligplaats.

    [Stelselpedia](http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/)
    """

    metadata_class = ExpansionMetadata
    queryset = models.Nummeraanduiding.objects.all()
    queryset_detail = models.Nummeraanduiding.objects.prefetch_related(
        Prefetch('verblijfsobject__panden',
                 queryset=models.Pand.objects.select_related('bouwblok'))
    ).select_related(
        'status',
        'openbare_ruimte',
        'openbare_ruimte__woonplaats',
        'verblijfsobject',
        'verblijfsobject__buurt',
        'verblijfsobject__buurt__buurtcombinatie',
        'verblijfsobject__buurt__stadsdeel',
    )
    serializer_detail_class = serializers.NummeraanduidingDetail
    serializer_class = serializers.Nummeraanduiding
    filter_class = NummeraanduidingFilter

    def retrieve(self, request, *args, **kwargs):
        """
        retrieve NummeraanduidingDetail

        ---

        serializer: serializers.NummeraanduidingDetail

        """

        return super().retrieve(
            request, *args, **kwargs)


