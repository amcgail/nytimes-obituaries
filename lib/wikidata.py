#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 12:51:31 2018

@author: alec
"""

from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

search_url = "https://www.wikidata.org/w/api.php?%s"

def subclassOf(what):
    # e.g. subclassOf("Q7210356") == political organization
    sparquery = """SELECT ?name
    WHERE
    {
         ?subClass (wdt:P279)* %s .
         ?theThing wdt:P31 ?subClass .
         ?theThing rdfs:label ?name .
         FILTER(LANG(?name) = "en")
    }
    """ % what

    sparql.setQuery(sparquery)
    r = sparql.query().convert()
    retNames = [x['name']['value'] for x in r['results']['bindings']]

    return retNames

def companyNames():
    csparquery = """SELECT ?clab
    WHERE
    {
         ?company rdfs:label ?clab .
         ?company wdt:P31 ?cinstanceOf .
         ?cinstanceOf wdt:P279* wd:Q783794 .
         FILTER(LANG(?clab) = "en")
    }
    """
    
    sparql.setQuery(csparquery)
    r = sparql.query().convert()

    cnames = [ x['clab']['value'] for x in r['results']['bindings'] ]

    return cnames

if "famousDict" not in locals():
    famousDict = {}

def lookupOccupationalTitles(name):
    import urllib
    import json

    if name in famousDict:
        return famousDict[name]
    
    query = {
        "action":"wbsearchentities",
        "search": name,
        "language":"en",
        "format":"json"
    }

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

    with urllib.request.urlopen( search_url % urllib.parse.urlencode(query) ) as response:
        r = json.loads(response.read().decode('utf-8'))
        if r['success'] != 1 or len(r['search']) == 0:
            return []
        
        myid = r['search'][0]['id']
        sparql.setQuery(sparquery % "wd:%s" % myid)
        r2 = sparql.query().convert()
        
        occs = set( [ x['occ']['value'] for x in r2['results']['bindings'] ] )
        famousDict[name] = occs
        return list(occs)