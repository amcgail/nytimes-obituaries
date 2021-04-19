from pymongo import MongoClient

DOC_DB = MongoClient()['nyt_obituaries']['documents']

noID = 0
total = 0
for doc in DOC_DB.find():
    total += 1
    if doc['wikiPageId'] is not None:
        print( "%s,%s,%s" % (doc['id'], doc['name'], doc['wikiPageId']) )
    else:
        noID += 1

print( noID / total )