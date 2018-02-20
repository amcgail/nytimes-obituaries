# -*- coding: utf-8 -*-
import urllib
import json

import csv
import sys
from os import path
#sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )
#from lib import *

from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

search_url = "https://www.wikidata.org/w/api.php?%s"

sparquery = """SELECT ?occ
WHERE
{
	%s wdt:P106 ?mainOcc .
     ?mainOcc (wdt:P279)* ?superOcc .
     ?superOcc rdfs:label ?occ .
     ?superOcc wdt:P31 wd:Q28640 .
     FILTER(LANG(?occ) = "en")
}
"""

alreadySearched = set()

outFn = path.join( path.dirname(__file__), "lookthemallup.wiki.txt" )

inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )
csv.field_size_limit(500 * 1024 * 1024)
with open(outFn, 'w') as outF:
    
    outCSV = csv.DictWriter(outF, ["fn","words","first500"])
    outCSV.writeheader()
    with open(inFn) as inF:
    
        success = 0
        fail = 0
        i = 0
        for l in csv.DictReader(inF):
            i += 1
            if i % 10 == 0:
                print(i, "done")
            
            name = l['name']
            name = name.replace( "Late Edition - Final\n", "" )
            name = name.replace( "Correction Appended\n", "" )
            name = name.replace( "The New York Times on the Web\n", "" )
            name = name.replace( "National Edition\n", "" )
            name = name.strip()
            
            if name == '':
                fail += 1
                continue
            
            if name in alreadySearched:
                fail += 1
                continue
            
            alreadySearched.add( name )
            
            query = {
                "action":"wbsearchentities",
                "search": name,
                "language":"en",
                "format":"json"
            }
            
            with urllib.request.urlopen( search_url % urllib.parse.urlencode(query) ) as response:
                r = json.loads(response.read().decode('utf-8'))
                if r['success'] != 1 or len(r['search']) == 0:
                    #print('fail!', name)
                    fail += 1
                    continue
                
                myid = r['search'][0]['id']
                sparql.setQuery(sparquery % "wd:%s" % myid)
                r2 = sparql.query().convert()
                
                occs = set( [ x['occ']['value'] for x in r2['results']['bindings'] ] )
                if len(occs) == 0:
                    fail += 1
                    continue
                
                #toWrite = name + "\n" + l['first500'] + "\n" + str(occs) + "\n\n\n\n"
                #outF.write(toWrite.encode('utf-8'))
                #print(toWrite)
                success += 1            
            
                outCSV.writerow( {
                    "fn": l['fName'],
                    "words": json.dumps(list(occs)),
                    "first500": l['first500']
                } )