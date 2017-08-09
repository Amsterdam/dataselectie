# Project
from . import fixture_utils
from datasets.bag.tests import fixture_utils as bag_factory
from datasets.hr.models import DataSelectie


def dataselectie_hr_factory(nummeraanduiding_obj, from_nr, to_nr):
    for json in fixture_utils.JSON[from_nr:to_nr]:
        id = json['vestigingsnummer']
        DataSelectie.objects.get_or_create(
            id=id,
            api_json=json,
            bag_numid=nummeraanduiding_obj.landelijk_id)


def create_hr_data():
    nummeraanduidingen = bag_factory.create_nummeraanduiding_fixtures()
    dataselectie_hr_factory(nummeraanduidingen[1], 0, 2)
    dataselectie_hr_factory(nummeraanduidingen[3], 2, 3)
    dataselectie_hr_factory(nummeraanduidingen[4], 3, 4)
    dataselectie_hr_factory(nummeraanduidingen[2], 4, 6)
