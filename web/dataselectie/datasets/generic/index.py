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


def chunck_qs_by_id(qs, chuncks=1000):
    """
    Determine ID range, chunck up range.
    """
    if not qs.count():
        return []

    # incase of string -> 00003
    # we must return length
    width = 0

    if isinstance(qs.first().id, str):
        width = len(qs.first().id)

    min_id = int(qs.first().id)
    max_id = int(qs.last().id)

    delta_step = int((max_id - min_id) / chuncks) or 1

    log.debug(
        'id range %s %s, chunksize %s', min_id, max_id, delta_step)

    steps = list(range(min_id, max_id, delta_step))
    # add max id range (bigger then last_id)
    steps.append(max_id+1)
    return steps, width


def return_qs_parts(qs, modulo, modulo_value):
    """ generate qs within min_id and max_id

        modulo and modulo_value determin which chuncks
        are teturned.

        if partial = 1/3

        then this function only returns chuncks index i for which
        modulo i % 3 == 1
    """
    chuncks = 1000

    if modulo > 1000:
        chuncks = modulo

    steps, width = chunck_qs_by_id(qs, chuncks)

    for i in range(len(steps)-1):
        if not i % modulo == modulo_value:
            continue

        start_id = steps[i]
        end_id = steps[i+1]

        print(width)

        if width:
            # deal with string values as pk
            start_id = f'%0{width}d' % start_id
            end_id = f'%0{width}d' % end_id

        qs_s = qs.filter(id__gte=start_id).filter(id__lt=end_id)

        count = qs_s.count()

        log.debug(
            '%4d Count: %s range %s %s',
            i, qs_s.count(), start_id, end_id)

        if count == 0:
            continue

        yield qs_s, i/1000.0

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
