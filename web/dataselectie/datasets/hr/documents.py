# Python
from typing import List, cast
# Packages
import elasticsearch_dsl as es
import json
# Project
from datasets.bag import models
from datasets.generic import analyzers


class sbicodeMeta(es.DocType):
    """
    Elastic doc for all meta of companies with sbicode.
    Used in the dataselectie portal
    """

    def __init__(self, *args, **kwargs):
        super(sbicodeMeta, self).__init__(*args, **kwargs)

    sbi_code = es.String(index='not_analyzed')
    sbi_categorie = es.String(index='not_analyzed')
    sbi_hoofdcategorie = es.String(index='not_analyzed')
    
    
def meta_from_json(jsondata: str, jsondata_paths: List[str]) -> dict:
    """
    Prepare data from json for use in elastic
    
    :param jsondata: Received jsondata from the dataselection subsystem
    :param jsondata_paths: list of paths to a specific field in
                            the format field1/field2/field3
    :return:
    """
    result = {}
    for jp in jsondata_paths:
        splitjppath = jp.split('/')
        result[splitjppath[-1]] = _recursepath(jsondata, splitjppath)

    return result

        
def _recursepath(jsondata: str, splitjppath: List[str]):
    """
    Recurse through jsondata and return value of a field
    :param jsondata:
    :param splitjppath:
    :return:
    """
    if len(splitjppath) > 1:
        return _recursepath(jsondata[splitjppath[0]], splitjppath[1:])
    else:
        return jsondata[splitjppath[0]]
    

def cleanjson(jsondata: str) -> str:
    """
    Remove headers put there by picklejson
    :param jsondata:
    :return: clean_json
    """