import factory
from factory import fuzzy
import random
import rapidjson
from .. import models
from . import fixture_utils


def DataSelectieHrFactory(vbobj, from_nr, to_nr):
    hrs = []
    for json in fixture_utils.JSON[from_nr:to_nr]:
        id = rapidjson.loads(json)['vestigingsnummer']
        hrdoc = models.DataSelectie.objects.get_or_create(id=id, api_json = json, bag_vbid = vbobj.landelijk_id)
        hrs.append(hrdoc)
    return hrs
