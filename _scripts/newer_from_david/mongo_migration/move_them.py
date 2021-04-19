from os.path import join, dirname
import sys
sys.path.append( join( dirname(__file__), '../../lib' ) )
from pymongo import MongoClient
import occ

DOC_DB = MongoClient()['nyt_obituaries']['documents']
#DOC_DB.drop()

excluded = ["human_name", "wiki_pageO"]

def clean(value):
    if type(value) in [list, set, frozenset]:
        return [ clean(x) for x in value ]
    if type(value) == dict:
        return {k:clean(v) for k,v in value.items()}
    return value

for obit in occ.obitIterator("older"):
    to_insert = {
        k: clean(v)
        for (k,v) in obit._prop_cache.items()
        if k not in excluded
    }

    #print(to_insert)
    id = DOC_DB.insert_one(to_insert)
    print(id.inserted_id)
