# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 03:03:27 2017

@author: alec
"""

from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

query = """SELECT ?child
WHERE
{
  # either this...
  ?child parent Bach.
  # or this...
  ?child father Bach.
  # or this.
  Bach child ?child.
  # (note: everything after a ‘#’ is a comment and ignored by WDQS.)
}"""

query = """
SELECT ?band ?bandLabel
WHERE
{
	?band  wdt:P31 wd:Q5741069 .
        ?band rdfs:label ?bandLabel .
	FILTER(STRSTARTS(?bandLabel, 'M')) .
}
"""

# never comes back
query = """
SELECT ?item ?itemLabel
WHERE
{
    ?item rdfs:label ?itemLabel .
    FILTER(STRSTARTS(?itemLabel, "New York Philharmonic")) .
}
"""

# comes back in a couple seconds
query = """
SELECT ?item ?itemLabel
WHERE
{
    ?item wdt:P31 ?itemClass .
    ?itemClass wdt:P31 wd:Q20202269 .
    ?item rdfs:label ?itemLabel .
    FILTER(STRSTARTS(?itemLabel, "New York Philharmonic")) .
}
"""

# takes about 4 seconds
query = """
SELECT ?corp ?corpName
WHERE
{
    ?corp wdt:P31 wd:Q4830453 .
    ?corp rdfs:label ?corpName .
    FILTER(STRSTARTS(?corpName, "RCA")) .    
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""

# so much quicker... why?
query = """
SELECT ?item ?itemLabel ?_image ?_subclass_of ?_subclass_ofLabel
WHERE
{
  ?item wdt:P31 wd:Q188451.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  OPTIONAL { ?item wdt:P279 ?_subclass_of. }
  OPTIONAL { ?item wdt:P18 ?_image. }
}
"""

#OMG! this one takes 4 seconds
query = """
#Streets named after a person
SELECT ?street ?streetLabel ?cityLabel ?personLabel
WHERE
{
    # ?street is a street
    ?street wdt:P31 wd:Q79007 .
    
    # ?street is in France
    ?street wdt:P17 wd:Q142 .
    
    # ?street is in ?city
    ?street wdt:P131 ?city .
    
    # ?street is named after ?person
    ?street wdt:P138 ?person .
    
    # ?person is human
    ?person wdt:P31 wd:Q5
    
    SERVICE wikibase:label { bd:serviceParam wikibase:language "fr" }
}
ORDER BY ?city
"""

# takes about 4 seconds
# gimme all US corporations founded in the year 1917
query = """
    SELECT distinct ?itemLabel
    WHERE
    {
        ?corp rdfs:label ?itemLabel .
        ?corp wdt:P31 wd:Q4830453 .
        ?corp wdt:P17 wd:Q30 .
        ?corp wdt:P571 ?inception_date .
        FILTER(year(?inception_date) = 1917) .
        FILTER(LANG(?itemLabel) = "en") .
    }
LIMIT 10000
"""

# go get all musical instruments!
query = """
    SELECT distinct ?itemLabel
    WHERE
    {
        ?inst rdfs:label ?itemLabel .
        ?inst wdt:P279 wd:Q34379 .
        MINUS { ?inst wdt:P31 wd:Q1254773 } .
        FILTER(LANG(?itemLabel) = "en") .
    }
LIMIT 500
"""

#just woodWind Instruments
query = """
    SELECT distinct ?itemLabel
    WHERE
    {
        ?inst rdfs:label ?itemLabel .
        ?inst wdt:P279 wd:Q173453 .
        MINUS { ?inst wdt:P31 wd:Q1254773 } .
        FILTER(LANG(?itemLabel) = "en") .
    }
LIMIT 500
"""


sparql.setQuery(query)
results = sparql.query().convert()

for r in results['results']['bindings']:
    if r["itemLabel"]["xml:lang"] == "en":
        print(r["itemLabel"]["value"])