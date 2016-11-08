import factory
from factory import fuzzy
import random
import rapidjson
from .. import models
from . import fixture_utils

# class HandelsRegisterFactory(factory.DjangoModelFactory):
#     class Meta:
#         model = models.HandelsRegister
#
#     api_json = fixture_utils.JSON[random.randint(0,3)]
#     id = int(rapidjson.loads(api_json)['vestigingsnummer'])
