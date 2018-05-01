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

cities = list(DictReader(open("world-cities_csv.csv")))
cities = list(set(map(getName, cities)))

fail = 0
success = 0
    
if True:
        
    csv.field_size_limit(500 * 1024 * 1024)
    inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )
    
    print("Extracting docs...")
    with open(inFn) as inF:
        docs = [ x['fullBody'] for x in csv.DictReader(inF) ]
    
    docs = random.sample( docs, 100 )
            
    wordCV = CountVectorizer()
    wordCdoc = wordCV.fit_transform( docs )
    words = wordCV.get_feature_names()
    wordCword = wordCdoc.sum( axis=1 )
    wordCdoc = wordCdoc.sum( axis=0 )
        
    wordGraph = []
        
    print("Constructing city-based graph")
    
    def isLetter(c):
        return ord(c) >= 65 and ord(c) <= 122
    
    for i,d in enumerate(docs):
        if (i+1) % 100 == 0:
            print(i, "of", len(docs), "done")
           
        for c in cities:
            findIt = d.find(c)
            if findIt < 0:
                continue
            
            if isLetter( d[findIt-1] ):
                continue
            
            
            ss = max(0, findIt-30)
            se = findIt+30
            print( c, ':', d[ss:se] )
            
            wordGraph.append( (i, c) )
    
    whatItIsC = Counter()
    
    wordsingraph = [x[1] for x in wordGraph]
    
# POST PROCESSING    
    
nounChunks = [x[1] for x in wordGraph]
chunkCounter = Counter(nounChunks)
#nounChunks = [x for x in nounChunks if 'human' in lookup(x)]
print("Found 'places'")
print( set(nounChunks) )

referentGraph = []
for d1,c1 in wordGraph:
    
    for c2 in nounChunks:
        
        if c1 == c2:
            continue
        
        if (d1,c2) in wordGraph:        
            if c1 > c2:
                referentGraph.append( (c1, c2) )
            else:
                referentGraph.append( (c2, c1) )
    
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

