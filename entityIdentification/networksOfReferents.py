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
    
    
    
    
    
if True:
        
    csv.field_size_limit(500 * 1024 * 1024)
    inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )
    
    print("Extracting docs...")
    with open(inFn) as inF:
        docs = [ x['fullBody'] for x in csv.DictReader(inF) ]
    
    #docs = random.sample( docs, 1000 )
            
    wordCV = CountVectorizer()
    wordCdoc = wordCV.fit_transform( docs )
    words = wordCV.get_feature_names()
    wordCword = wordCdoc.sum( axis=1 )
    wordCdoc = wordCdoc.sum( axis=0 )
        
    wordGraph = set()
        
    j = 0
    print("Constructing noun-based graph")
    for i,d in enumerate(docs):
        if "Jack" not in d or "Nicholson" not in d:
            continue
        
        #j += 1
        #doc = nlp(d)
        #print( [x for x in doc.sents if "Nicholson" in str(x)] )
        
        #continue
    
        doc = nlp(d)
        if (i+1) % 100 == 0:
            print(i, "of", len(docs), "done")
        
        verbGroup = {}
        
        for chunk in doc.noun_chunks:
        
            ch = chunk.text
            ch.replace("\n", " ")
            ch.replace("  ", " ")
            ch = ch.strip()
            
            chunk = list(chunk)
            chunk = [ x for x in chunk if x.pos_ != 'SPACE' ]

            # expand if necessary
            nextWord = chunk[-1]
            if nextWord.i+1 < len(nextWord.doc):
                nextWord = nextWord.doc[ nextWord.i + 1 ]
                while str(nextWord).lower() != str(nextWord) or nextWord.pos_ == 'SPACE':
                    if nextWord.pos_ != 'SPACE':
                        chunk.append(nextWord)
                        # print("expanding: ", chunk, nextWord)
    
                    if nextWord.i+1 >= len(nextWord.doc):
                        break
                    
                    nextWord = nextWord.doc[ nextWord.i + 1 ]
                
            ch = " ".join( [str(w) for w in chunk] )
            
            #if ch.lower() in words and wordCdoc[0,words.index(ch.lower())] > len(docs)*0.1:
            #    continue
            if ch == ch.lower():
                continue
            
            ch = " ".join( ch.split() )
            
            wordGraph.add( (i, ch) )

if False:
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
    

nounChunks = [x[1] for x in wordGraph]

import gender_guesser.detector as gender
g = gender.Detector()

def isname(x):
    if len( x.split() ) > 1:
        return any([isname(y) for y in x.split()])
        
    # if any word has a gender, we good    
    return g.get_gender(x) != 'unknown'

nounChunks = list(filter( isname, nounChunks ))

if False:
    # POST PROCESSING. filters out everything that's not a name... takes quite a while
    
    chunkCounter = Counter(nounChunks)
    nounChunks = [x for x in nounChunks if chunkCounter[x] > 1]
    nounChunks = [ x for x in nounChunks if len(x.split()) > 1 ]
    nounChunks = [x for x in nounChunks if 'human' in lookup(x)]

wordGraph = list(set(wordGraph))

referentGraph = []
for d1,c1 in wordGraph:
    if c1 not in nounChunks:
        continue
    
    for c2 in nounChunks:
        if c1 == c2:
            continue
        
        if (d1,c2) in wordGraph:        
            if c1 > c2:
                referentGraph.append( (c1, c2) )
            else:
                referentGraph.append( (c2, c1) )

def okForGraph(x):
    noNoWords = ["the","university","city"]
    ws = x.lower().split()
    
    for nnw in noNoWords:
        if nnw in ws:
            return False
        
    if not x.istitle(): # awesome that this exists
        return False
    if len(x.split()) == 1:
        return False
    if not any( isname(y) for y in x.split()[:-1] ):
        return False
    return True

if False:
    # do it again!?
    
    newreferentGraph = []            
    for i, (x,y) in enumerate( referentGraph ):
        if i % 5 == 0:
            print(i," of ",len(referentGraph)," done")
        if "the" in x.lower() or "the" in y.lower():
            continue
        if 'human' in lookup(x) and 'human' in lookup(y):
            newreferentGraph.append((x,y))
        
    referentGraph = [(x,y) for (x,y) in referentGraph if 'human' in lookup(x) and 'human' in lookup(y)]
    referentGraph = Counter(referentGraph)

referentGraphAg = Counter(referentGraph)
referentGraphAg = {x: referentGraphAg[x] for x in referentGraphAg if okForGraph(x[0]) and okForGraph(x[1])}
#referentGraph = list( filter( lambda x: , referentGraph ) )

graphCSV = [
    {
     "Source": x[0],
     "Target": x[1],
     "weight": y
    }
    for (x,y) in referentGraphAg.items()
]

from csv import DictWriter

with open('referentGraph.csv','w') as csvf:
    dw = DictWriter(csvf, ('Source','Target','weight'))
    dw.writeheader()
    dw.writerows(graphCSV)

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

