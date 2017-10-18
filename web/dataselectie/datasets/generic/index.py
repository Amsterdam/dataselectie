# Python
import logging
import time
# Packages
from django.conf import settings
from django.db.models.functions import Cast
from django.db.models import F
from django.db.models import BigIntegerField

import elasticsearch
from elasticsearch import helpers
from elasticsearch.exceptions import NotFoundError
import elasticsearch_dsl as es
from elasticsearch_dsl.connections import connections

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


def return_qs_parts(qs, modulo, modulo_value):
    """
    build qs

    modulo and modulo_value determin which chuncks
    are teturned.

    if partial = 1/3

    then this function only returns chuncks index i for which
    modulo i % 3 == 1
    """

    qs_s = (
        qs
        .annotate(intid=Cast('id', BigIntegerField()))
        .annotate(idmod=F('intid') % modulo)
        .filter(idmod=modulo_value-1)
    )

    qs_count = qs_s.count()
    log.debug(f'PART {modulo_value}/{modulo} {qs_count}')

    for i in range(0, qs_count+1000, 1000):

        if i > qs_count:
            qs_ss = qs_s[i:]
        else:
            qs_ss = qs_s[i:i+1000]

        log.debug('Batch %4d %4d', i, i + 1000)

        yield qs_ss, i/qs_count

    raise StopIteration


class ImportIndexTask(object):
    queryset = None

    client = elasticsearch.Elasticsearch(
        hosts=settings.ELASTIC_SEARCH_HOSTS,
        retry_on_timeout=True,
    )

    index = None

    def get_queryset(self):
        return self.queryset.order_by('id')

    def convert(self, obj):
        raise NotImplementedError()

    def batch_qs(self):
        """
        Returns a (start, end, total, queryset) tuple
        for each batch in the given queryset.

        Usage:
            # Make sure to order your querset!
            article_qs = Article.objects.order_by('id')
            for qs in batch_qs(article_qs):
                for article in qs:
                    print article.body
        """
        qs = self.get_queryset()

        log.info('ITEMS %d', qs.count())

        # batch_size = settings.BATCH_SETTINGS['batch_size']
        numerator = settings.PARTIAL_IMPORT['numerator']
        denominator = settings.PARTIAL_IMPORT['denominator']

        log.info("PART: %s OF %s", numerator + 1, denominator)

        for qs_p, progres in return_qs_parts(qs, denominator, numerator):
            yield qs_p, progres

    def execute(self):
        """
        Index data of specified queryset
        """
        start_time = time.time()

        for qs, progress in self.batch_qs():

            elapsed = time.time() - start_time

            total_left = (1 / (progress + 0.001)) * elapsed - elapsed

            progres_msg = \
                '%.3f : duration: %.2f left: %.2f' % (
                    progress, elapsed, total_left
                )

            log.info(progres_msg)

            helpers.bulk(
                self.client,
                (self.convert(obj).to_dict(include_meta=True) for obj in qs),
                raise_on_error=True,
            )

        if settings.IN_TEST_MODE and self.index:
            idx = es.Index(self.index)
            # refresh index, make sure its ready for queries
            idx.refresh()
