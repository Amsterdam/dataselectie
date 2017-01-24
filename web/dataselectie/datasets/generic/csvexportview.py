# Python
import codecs
from typing import Generator
import csv
import logging
from datetime import datetime
import io
# Packages
from django.conf import settings
from django.db.models.fields.related import ManyToManyField
from django.http import StreamingHttpResponse
from elasticsearch.helpers import scan
from pytz import timezone
# Project
from datasets.bag.models import Nummeraanduiding
from .tablesearchview import TableSearchView
from .tablesearchview import _stringify_item_value

log = logging.getLogger(__name__)


class CSVExportView(TableSearchView):
    """
    A base class to generate csv exports
    """
    # This is not relevant for csv export
    preview_size = None
    # The headers of the csv
    headers = []
    # The pretty version of the headers
    pretty_headers = []

    def get_queryset(self) -> Generator:
        """
        Instead of an actual queryset,
        it returns an elastic scroll api generator
        """
        query_string = self.request_parameters.get('query', None)
        # Building the query
        q = self.elastic_query(query_string)
        query = self.build_elastic_query(q)
        # Making sure there is no pagination
        if query is not None and 'from' in query:
            del (query['from'])

        # Returning the elastic generator
        return scan(
            self.elastic, query=query,
            index=settings.ELASTIC_INDICES[self.index])

    # TODO type es_generator
    def result_generator(self, es_generator, batch_size: int=100):
        """
        Generate the result set for the CSV eport
        """
        write_buffer = io.StringIO()  # The buffer to stream to
        writer = csv.DictWriter(write_buffer, self.headers, delimiter=';')
        more = True  # More results flag
        header_dict = {}  # A dict for the CSV headers
        for i in range(len(self.headers)):
            header_dict[self.headers[i]] = self.pretty_headers[i]

        # A func to read and empty the buffer
        def read_and_empty_buffer():
            write_buffer.seek(0)
            buffer_data = write_buffer.read()
            write_buffer.seek(0)
            write_buffer.truncate()
            return buffer_data

        # Yielding BOM for utf8 encoding
        yield codecs.BOM_UTF8
        # Yielding headers as first line
        writer.writerow(header_dict)
        yield read_and_empty_buffer()

        # Yielding results in batches of batch_size
        while more:

            items = {}
            # Collecting items for batch
            for item in es_generator:
                items = self._fill_item(items, item)
                # Breaking on batch size
                if len(items) >= batch_size:
                    break

            # Retrieving the database data

            qs = self.model.objects.filter(id__in=list(items.keys()))
            qs = self._convert_to_dicts(qs)

            # Pairing the data
            data = self._combine_data(qs, items)
            for item in data:
                # Only returning fields from the headers
                resp = {}
                for key in self.headers:
                    resp[key] = item.get(key, '')
                writer.writerow(resp)
            yield read_and_empty_buffer()

            # Stop the run, if end is reached
            more = len(items) >= batch_size

    def _convert_to_dicts(self, qs) -> list:
        """
        Converts every item in the queryset to a dict
        with property name as key and property value as value
        Overwrite this fnction for custom fields, or following
        relations
        """
        return [_model_to_dict(d) for d in qs]

    def _combine_data(self, data: list, es: dict) -> list:
        """
        Combines the elastic data with the
        data retrieved from the query
        """
        for item in data:
            # Making sure all the data is in string form
            item.update(
                {k: _stringify_item_value(v) for k, v in item.items() if
                 not isinstance(v, str) or v is None}
            )
            # Adding the elastic context
            for key, value in es[item['id']]['_source'].items():
                item[key] = value
        return data

    def _fill_item(self, items, item):
        """
        Function can be overwritten in the using class to allow for
        specific output (hr has multi outputs

        :param items:   Resulting dictionary containing the
        :param item:    Item from elastic
        :return: items
        """
        items[item['_id']] = item

        return items

    def render_to_response(self, context, **response_kwargs):
        # Returning a CSV
        # Streaming!
        gen = self.result_generator(context['object_list'])
        response = StreamingHttpResponse(gen, content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment; ' \
            'filename="export_{0:%Y%m%d_%H%M%S}.csv"'.format(datetime.now(
                tz=timezone('Europe/Amsterdam')))
        return response


def _model_to_dict(item: Nummeraanduiding) -> dict:
    """
    Converts a django model to a dict.
    It does not do a deep conversion
    """
    data = {}  # type dict[str, str]
    properties = item._meta
    for field in properties.concrete_fields + properties.many_to_many:
        if isinstance(field, ManyToManyField):
            data[field.name] = list(
                field.value_from_object(item).values_list('pk', flat=True))
        else:
            data[field.name] = field.value_from_object(item)
    return data
