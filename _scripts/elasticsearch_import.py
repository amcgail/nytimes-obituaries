from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

import sys
sys.path.append("../lib")

import occ
coder = occ.Coder()
coder.loadPreviouslyCoded("v2.0", N=100, rand=False)

for obit in coder.obituaries:
    es.index(index='sw', doc_type='obits', id=obit['id'], body=obit._prop_cache)

from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
es.indices.refresh(index="sw")
