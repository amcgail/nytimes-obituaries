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
    
inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )

print("Extracting docs...")
with open(inFn) as inF:
    docs = [ x['fullBody'] for x in csv.DictReader(inF) ]

docs = random.sample( docs, 2000 )
        
wordCV = CountVectorizer()
wordCdoc = wordCV.fit_transform( docs )
words = wordCV.get_feature_names()
wordCword = wordCdoc.sum( axis=1 )
wordCdoc = wordCdoc.sum( axis=0 )
    
wordGraph = set()
    
print("Constructing noun-based graph")
for i,d in enumerate(docs):
    doc = nlp(d)
    if (i+1) % 100 == 0:
        print(i, "done")
    
    verbGroup = {}
    
    for chunk in doc.noun_chunks:
        ch = chunk.text
        ch.replace("\n", " ")
        ch.replace("  ", " ")
        if ch.lower() in words and wordCdoc[0,words.index(ch.lower())] > len(docs)*0.1:
            continue
        if ch == ch.lower():
            continue
        
        wordGraph.add( (i, ch) )

#what are the more popular instances (included in more obits)?

search_url = "https://www.wikidata.org/w/api.php?%s"

sparquery = """SELECT ?lab
WHERE
{
    %s wdt:P31 ?instOf .
    ?instOf rdfs:label ?lab .
    FILTER(LANG(?lab) = "en")
}
"""

# ?instOf (wdt:P279)* ?superInstOf .

fail = 0
success = 0

searchResults = {}

def lookup(name):
    global searchResults
    global fail, success
    
    if name in searchResults:
        return searchResults[name]
    
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
            searchResults[name] = []
            return []

        labs = []                
                
        for res in r['search']:
            myid = res['id']
            sparql.setQuery(sparquery % "wd:%s" % myid)
            r2 = sparql.query().convert()
    
            labs += [ x['lab']['value'] for x in r2['results']['bindings'] ]
        
        if len(labs) == 0:
            fail += 1
            searchResults[name] = []
            return []        
        
        success += 1
        searchResults[name] = list(set(labs))
        return list(set(labs))

print("Looking everything up in WikiData")

whatItIsC = Counter()

wordsingraph = [x[1] for x in wordGraph]
multiword = [ x for x in wordsingraph if len(x.split()) > 1 ]
c = Counter( multiword )
for w, count in c.items():
    if count < 5:
        continue
    
    allInst = len([ x for x in docs if w.lower() in x.lower() ])
    lcInst = len([ x for x in docs if w.lower() in x ])
    if lcInst > 0.1*allInst:
        continue
    
    whatItIs = lookup(w)
    whatItIsC.update(whatItIs)
    
    print(w, count)
    
[ x for x in searchResults if 'scientific article' in searchResults[x] ]
[ x for x in searchResults if 'band' in searchResults[x] ]
[ x for x in searchResults if 'private university' in searchResults[x] ]
[ x for x in searchResults if 'census-designated place' in searchResults[x] ]
[ x for x in searchResults if 'university' in searchResults[x] ]
"""
['Wayne State University',
 'Pennsylvania State University',
 'Rockefeller University',
 'the National Institute',
 'Penn State',
 'the City College',
 "St. John's University",
 'Brown University',
 'the City University',
 'Hunter College',
 'Ithaca College',
 'West Virginia',
 'Indiana University',
 'Tufts University',
 'Smith College',
 'Boston College',
 'American University',
 'Emory University',
 'George Washington University',
 'Catholic University',
 'Washington University',
 'Adelphi University',
 'Radcliffe College',
 'Cambridge University',
 'Tel Aviv',
 'Long Island University',
 'Swarthmore College',
 'Queens College',
 'Johns Hopkins University',
 'Duke University',
 'Pratt Institute',
 'Columbia University',
 'Bennington College',
 'Pace University',
 'Trinity College',
 'Columbia College',
 'Yeshiva University',
 'McGill University',
 'New York University',
 'Northwestern University',
 'Fordham University',
 'Colgate University',
 'Cornell University',
 'Boston University',
 'St. Petersburg',
 'City College',
 'North Carolina']
"""