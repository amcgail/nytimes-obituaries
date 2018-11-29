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

fail = 0
success = 0

if 'searchResults' not in locals():
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
            if res['match']['text'].lower() != name.lower():
                continue
            
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
    
"""
CURRENT PROBLEMS:

names have to be expanded:
    Mr. Jones to James Earl Jones, where previously mentioned.
    NO! Just get rid of "Mr.". we only need one referent
    
the name of the guy himself has to be removed:

    first noun chunk seems to work:
    
    for d in docs:
        print(d[:150])
        doc = nlp(d)
        print(list(doc.noun_chunks)[0])
        print("")
        
Then I need to actually look them up to verify it's a name!
"""

abbrev = ["Mr.","Mrs.","Ms.","Dr."]
    
if True:
        
    csv.field_size_limit(500 * 1024 * 1024)
    inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )
    
    print("Extracting docs...")
    with open(inFn) as inF:
        docs = [ x['fullBody'] for x in csv.DictReader(inF) ]
    
    docs = random.sample( docs, 1000 )
            
    wordCV = CountVectorizer()
    wordCdoc = wordCV.fit_transform( docs )
    words = wordCV.get_feature_names()
    wordCword = wordCdoc.sum( axis=1 )
    wordCdoc = wordCdoc.sum( axis=0 )
        
    wordGraph = []
        
    print("Constructing noun-based graph")
    for i,d in enumerate(docs):
        doc = nlp(d)
        if (i+1) % 100 == 0:
            print(i, "of", len(docs), "done")
            
        #print(d)
        
        verbGroup = {}
        
        toAdd = set()
        
        first = True
        hisName = None
        for chunk in doc.noun_chunks:
            if first:
                print("skipping(first)", chunk)
                hisName = chunk
                first = False
                continue
            
            ch = chunk.text
            ch.replace("\n", " ")
            ch.replace("  ", " ")
            ch = ch.strip()

            # only if it's a name
            if not isname(ch):
                continue
            
            hasAbbrev = False
            for a in abbrev:
                if a in ch:
                    hasAbbrev = True
            if hasAbbrev and len(ch.split()) < 3:
                continue
            
            if 'the' in [x.lower() for x in ch.split()]:
                continue
            
            if not all([x.lower() != x for x in ch.split()]):
                continue
            
            chunk = list(chunk)
            chunk = [ x for x in chunk if x.pos_ != 'SPACE' ]

            # expand if necessary
            nextWord = chunk[-1]
            nextWord = nextWord.doc[ nextWord.i + 1 ]
            while str(nextWord).lower() != str(nextWord) or nextWord.pos_ == 'SPACE':
                if nextWord.pos_ != 'SPACE':
                    chunk.append(nextWord)
                    print("expanding: ", chunk, nextWord)

                if nextWord.i+1 >= len(nextWord.doc):
                    break
                
                nextWord = nextWord.doc[ nextWord.i + 1 ]
                
            ch = " ".join( [str(w) for w in chunk] )
            
            #if ch.lower() in words and wordCdoc[0,words.index(ch.lower())] > len(docs)*0.1:
            #    continue
            if ch == ch.lower():
                continue
            
            toAdd.update([ch])
        
        #print(toAdd)
        
        for ch in toAdd:
            wordGraph.append( (i, ch) )
    
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
    
    
    
    
    
# POST PROCESSING    
    
nounChunks = [x[1] for x in wordGraph]
chunkCounter = Counter(nounChunks)
nounChunks = [x for x in nounChunks if chunkCounter[x] > 1]
nounChunks = [ x for x in nounChunks if len(x.split()) > 1 ]
#nounChunks = [x for x in nounChunks if 'human' in lookup(x)]
print("Found 'people'")
print( set(nounChunks) )

referentGraph = []
for d1,c1 in wordGraph:
    if c1 not in nounChunks:
        continue
    if not isname(c1):
        continue
    
    for c2 in nounChunks:
        if c2 not in nounChunks:
            continue
        if not isname(c2):
            continue
        
        if c1 == c2:
            continue
        
        if (d1,c2) in wordGraph:        
            if c1 > c2:
                referentGraph.append( (c1, c2) )
            else:
                referentGraph.append( (c2, c1) )

tipoffs = ["city","the"]

newreferentGraph = []            
for i, (x,y) in enumerate( referentGraph ):
    if i % 15 == 0:
        print(i," of ",len(referentGraph)," done")
        
    getOut = False
    for t in tipoffs:
        if t in x.lower() or t in y.lower():
            getOut = True
    if getOut:
        continue
    
    print(x,y)
    if 'human' in lookup(x) and 'human' in lookup(y):
        newreferentGraph.append((x,y))
        
referentGraph = [(x,y) for (x,y) in referentGraph if 'human' in lookup(x) and 'human' in lookup(y)]
referentGraph = Counter(referentGraph)
    
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
...
 'Colgate University',
 'Cornell University',
 'Boston University',
 'St. Petersburg',
 'City College',
 'North Carolina']
"""

