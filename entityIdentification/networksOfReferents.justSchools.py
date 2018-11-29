# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
import urllib
import json

from collections import Counter

import csv
import sys
from os import path

from nltk import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import RidgeClassifierCV

from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

import spacy
import numpy as np

import random

#sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )
#from lib import *

if 'nlp' not in locals():
    print("nlp not found in global namespace. Loading...")
    print("NOTE: this variable is huge, and can eat up memory. Don't load in multiple terminals.")
    nlp = spacy.load('en')
    
    
    
    
import gender_guesser.detector as gender
g = gender.Detector()

def isname(x):
    if len( x.split() ) > 1:
        return any([isname(y) for y in x.split()])
        
    # if any word has a gender, we good    
    return g.get_gender(x) in ['male', 'female']



from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

geolocator = Nominatim()

    
    
search_url = "https://www.wikidata.org/w/api.php?%s"

sparquery = """SELECT ?lab
WHERE
{
    %s wdt:P31 ?instOf .
    ?instOf rdfs:label ?lab .
    FILTER(LANG(?lab) = "en")
}
"""

def getName(c):
    if c['country'] == 'United States':
        return c['name'] + ', ' + c['subcountry'][:2]
    
    return c['name'] + ', ' + c['country'][:2]

def getLongName(c):
    if c['country'] == 'United States':
        return c['name'] + ', ' + c['subcountry']
    
    return c['name'] + ', ' + c['country']

unis = list(DictReader(open("world-universities.csv"), fieldnames=["a","name","website"]))
# cities = list(set(map(getName, cities)))

fail = 0
success = 0
    
csv.field_size_limit(500 * 1024 * 1024)
inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )

print("Extracting docs...")
with open(inFn) as inF:
    docs = list( csv.DictReader(inF) )

docs = random.sample( docs, 10000 )
        
wordGraph = []
    
print("Constructing school-based graph")

buffer = 80

def isLetter(c):
    return ord(c) >= 65 and ord(c) <= 122

for i,ev in enumerate(docs):
    d = ev['fullBody']
    
    if (i+1) % 100 == 0:
        print(i, "of", len(docs), "done")
       
    for u in unis:
        c = u['name']
        
        findIt = d.find(c)
        if findIt < 0:
            continue
        
        if isLetter( d[findIt-1] ):
            continue
        
        ss = max(0, findIt-buffer)
        se = findIt+buffer
        
        #print( c, "(%s/%s) = %.04f%%"%(findIt,len(d),float(findIt)/len(d)), ':', d[ss:se] )
        
        wordGraph.append( (i, c) )
    
# POST PROCESSING    
    
nounChunks = [x[1] for x in wordGraph]
chunkCounter = Counter(nounChunks)
#nounChunks = [x for x in nounChunks if 'human' in lookup(x)]
print("Found 'places'")
print( set(nounChunks) )
    
"""
['Wayne State University',
 'Pennsylvania State University',
 'Rockefeller University',
 'the National Institute',
 'Penn State',
...
 'Colgate University',
 'Cornell University',
 'Boston University',
 'St. Petersburg',
 'City College',
 'North Carolina']
"""

with open('obitLocations.csv', 'w') as locOut:
    csvW = writer(locOut)
    csvW.writerow(["fn","date","lat","lon","cname"])
    for r in wordGraph:
        csvW.writerow(list(r))