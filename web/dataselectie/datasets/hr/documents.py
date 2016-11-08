# Python
from typing import List, cast
# Packages
import elasticsearch_dsl as es
import rapidjson
# Project
from . import models
from datasets.generic import analyzers


# class HandelsregisterMeta(es.DocType):
#     """
#     Elastic doc for all meta of companies with sbicode.
#     Used in the dataselectie portal
#     """
#
#     def __init__(self, *args, **kwargs):
#         super(HandelsregisterMeta, self).__init__(*args, **kwargs)
#
#     vestigingsnummer_id = es.String(index='not_analyzed')
#     nummeraanduiding_id = es.String(index='not_analyzed')
#     sbi_codes = es.Object()
#
#
# def meta_from_handelsregister(item: models.HandelsRegister) -> dict:
#
#     doc = HandelsregisterMeta(_id=item.id)
#     api_dict = rapidjson.loads(item.api_json)
#     doc.nummeraanduiding_id = api_dict['bezoekadres']['bag_nummeraanduiding']
#     if not doc.nummeraanduiding_id:
#         doc.nummeraanduiding_id = api_dict['postadres']['bag_nummeraanduiding']
#     doc.sbi_codes = api_dict['sbi_codes']
