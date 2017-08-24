# Python
import logging
import time
# Packages
from django.conf import settings
import elasticsearch
from elasticsearch import helpers
from elasticsearch.exceptions import NotFoundError
import elasticsearch_dsl as es
from elasticsearch_dsl.connections import connections

from batch import batch

log = logging.getLogger(__name__)


class DeleteIndexTask(object):
    index = ''  # type: str
    doc_types = []
    name = 'remove index'

    def __init__(self):

        if not self.index:
            raise ValueError("No index specified")

        if not self.doc_types:
            raise ValueError("No doc_types specified")

        connections.create_connection(
            hosts=settings.ELASTIC_SEARCH_HOSTS,
            retry_on_timeout=True,
        )

    def execute(self):

        idx = es.Index(self.index)

        try:
            idx.delete(ignore=404)
            log.info("Deleted index %s", self.index)
        except AttributeError:
            log.warning("Could not delete index '%s', ignoring", self.index)
        except NotFoundError:
            log.warning("Index '%s' not found, ignoring", self.index)


class CreateDocTypeTask(object):
    index = ''  # type: str
    doc_types = []
    name = 'Create Doctypes in index'

    def __init__(self):

        if not self.index:
            raise ValueError("No index specified")

        if not self.doc_types:
            raise ValueError("No doc_types specified")

        connections.create_connection(
            hosts=settings.ELASTIC_SEARCH_HOSTS,
            retry_on_timeout=True,
        )

    def execute(self):

        idx = es.Index(self.index)

        for dt in self.doc_types:
            idx.doc_type(dt)

        idx.create()


class ImportIndexTask(object):
    queryset = None

    client = elasticsearch.Elasticsearch(
        hosts=settings.ELASTIC_SEARCH_HOSTS,
        # sniff_on_start=True,
        retry_on_timeout=True,
        refresh=True
    )

    def get_queryset(self):
        return self.queryset.order_by('id')
        # return self.queryset.iterator()

    def convert(self, obj):
        raise NotImplementedError()

    def batch_qs(self):
        """
        Returns a (start, end, total, queryset) tuple
        for each batch in the given queryset.

        Usage:
            # Make sure to order your querset!
            article_qs = Article.objects.order_by('id')
            for start, end, total, qs in batch_qs(article_qs):
                print "Now processing %s - %s of %s" % (start + 1, end, total)
                for article in qs:
                    print article.body
        """
        qs = self.get_queryset()

        batch_size = settings.BATCH_SETTINGS['batch_size']
        numerator = settings.PARTIAL_IMPORT['numerator']
        denominator = settings.PARTIAL_IMPORT['denominator']

        log.info("PART: %s OF %s", numerator + 1, denominator)

        end_part = count = total = qs.count()
        chunk_size = total

        start_index = 0

        # Do partial import
        if denominator > 1:
            chunk_size = int(total / denominator)
            start_index = numerator * chunk_size
            # for the last part do not change end_part
            if denominator > numerator+1:
                end_part = (numerator + 1) * chunk_size
            total = end_part - start_index

        log.info(f'START: {start_index} END {end_part} COUNT: {chunk_size} CHUNK {batch_size} TOTAL_COUNT: {count}')  # noqa
        # total batches in this (partial) bacth job
        total_batches = chunk_size / batch_size
        for i, start in enumerate(range(start_index, end_part, batch_size)):
            end = min(start + batch_size, end_part)
            yield (i + 1, total_batches + 1, start, end, total, qs[start: end])

    def execute(self):
        """
        Index data of specified queryset
        """
        start_time = time.time()
        loop_time = elapsed = time.time() - start_time
        loop_times = [1]

        for batch_i, total_batches, start, end, total, qs in self.batch_qs():

            loop_start = time.time()
            avg_loop_time = sum(loop_times) / float(len(loop_times))
            total_left = ((total_batches - batch_i) * avg_loop_time) + 1 / 60

            progres_msg = \
                '%s of %.1f : %8s %8s %8s duration: %.2f left: %.2f batchtime %.2f' % (    # noqa
                    batch_i, total_batches, start, end, total, elapsed,
                    total_left, avg_loop_time
                )

            log.info(progres_msg)

            helpers.bulk(
                self.client,
                (self.convert(obj).to_dict(include_meta=True) for obj in qs),
                raise_on_error=True,
                refresh=True
            )

            elapsed = time.time() - start_time
            loop_time = time.time() - loop_start
            loop_times.append(loop_time)

            if len(loop_times) > 15:
                loop_times.pop(0)

        batch.statistics.report()
