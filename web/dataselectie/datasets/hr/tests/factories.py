
from .. import models
from . import fixture_utils


def dataselectiehrfactory(vbobj, from_nr, to_nr):
    hrs = []
    for json in fixture_utils.JSON[from_nr:to_nr]:
        id = json['vestigingsnummer']
        hrdoc = models.DataSelectie.objects.get_or_create(
            id=id, api_json=json, bag_numid=vbobj.landelijk_id, bag_vbid=vbobj.openbare_ruimte_id)
        hrs.append(hrdoc)
    return hrs
