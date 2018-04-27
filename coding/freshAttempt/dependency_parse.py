# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

from collections import Counter

from nltk.corpus import wordnet as wn
from spacy.matcher import Matcher

import csv
from csv import reader, DictReader
from csv import QUOTE_MINIMAL
from nltk import sent_tokenize, word_tokenize
import nltk
from os import path
from collections import Counter
import numpy as np
import re
import sys
from itertools import chain

import urllib

basedir = path.join( path.dirname(__file__), '..', ".." )

sys.path.append( path.join( basedir, 'lib' ) )

from lib import *

if 'nlp' not in locals():
    import spacy
    nlp = spacy.load('en')

inFn = path.join( basedir, "data","extracted.all.nice.csv" )

debug = False

notCoded = []
coded = []

confidenceHist = []

csv.field_size_limit(500 * 1024 * 1024)


#==============================================================================
# months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
# months += [ m[:3] for m in months ]
# months += [ m[:3] + "." for m in months ]
# dayStr = "|".join( [ '"%s"' % i for i in range(31) ] )
# monthStr = "|".join( [ '"%s"' % i for i in months ] )
# places = ["home", "Manhattan"]
# placeStr = "|".join( [ '"%s"' % i for i in places ] )
# 
# grammar1 = nltk.CFG.fromstring("""
#   Loc -> {placeStr}
#   Loc -> Loc "in" Loc
#   Month -> {monthStr}
#   Day -> {dayStr}
#   Date -> Month Day
#   Death -> "on" Date "at" Loc
#   Death -> "on" Date "in" Loc
# """.format(**locals()))
#==============================================================================

import re

pattern1 = [{'POS':'VERB', 'OP':'!'}, {'POS': 'CCONJ'}, {'POS': 'DET', 'OP':'?'}, {'POS': 'ADV', 'OP': "*"}, {'POS': 'ADJ', 'OP': "*"}, {'POS': 'NOUN', 'OP': "+"}]
pattern2 = [{'POS':'VERB', 'OP':'!'}, {'POS': 'DET'}, {'POS': 'ADV', 'OP': "*"}, {'POS': 'ADJ', 'OP': "*"}, {'POS': 'NOUN', 'OP': "+"}]
matcher = Matcher(nlp.vocab)
matcher.add('adjNoun', None, pattern1) # add pattern
matcher.add('adjNoun', None, pattern2) # add pattern

skipped = 0
#whwCount = Counter()

def posFind(seq, doc):
    i = 0
    for j, x in enumerate(doc):
        if x.pos_ == seq[i]:
            i += 1
        else:
            i = 0
            
        if i >= len(seq):
            return j+1-len(seq)
    return -1

def posSplit(seq, doc):
    i = 0
    splitAt = []
    for j, x in enumerate(doc):
        if x.pos_ == seq[i]:
            i += 1
        else:
            i = 0
            
        if i >= len(seq):
            splitAt.append( j+1-len(seq) )
            i = 0
    
    if len(splitAt) == 0:
        return doc
    
    splits = []
    lastJ = -1
    for j in splitAt:
        print(lastJ)
        if lastJ < 0:
            splits.append(doc[:j])
        else:
            splits.append(doc[lastJ:j])
        lastJ = j+len(seq)
    splits.append(doc[lastJ:])
    return splits

def synonyms(w):
    ss = wn.synsets(w, pos='n')

    if len(ss) == 0:
        return []
    
    def distanceToPerson(s):
        ds = s.hypernym_distances()
        for parent, d in ds:
            if parent == wn.synset('person.n.01'):
                return d
        
        # if it's not even a parent
        return -1
    
    # THIS PART IS HARD AND ERROR-PRONE
    if True:
        # take the most specific definition
        s = max( ss, key=distanceToPerson )
    
    if distanceToPerson(s) > 1:
        hypo = lambda s: s.hyponyms()
        hypos = list(s.closure(hypo))
        
        allS = [s]+hypos
    else:
        allS = [s]
    
    syns = [x.name() for y in allS for x in y.lemmas()]
    syns = [x for x in syns if '_' not in x and x.lower() == x]
    
    return list(set(syns))

sCount = Counter()

nw2c = {}

w2c['professor'] = ['occ2000-220']
w2c['writer'] = ['occ2000-285']
w2c['photographer'] = ['occ2000-291']
w2c['filmmaker'] = ['occ2000-271']

for k,codes in w2c.items():
    if len(k.split()) != 1:
        continue
    
    def fCode(c):
        try:
            n = int(c.lower().split("occ2000-")[1])
        except ValueError:
            return False
            
        if n > 620 and n < 900:
            return False
        return True
    
    nc = [c for c in codes if 'occ2000' in c]
    nc = list(filter(fCode, nc))
    if len(nc) == 0:
        continue
    
    nw2c[k] = nc
        
# now expand this vocabulary with synonyms:
synMap = {}

for k,v in nw2c.items():
    syn = synonyms(k)
    
    synCodes = [ nw2c[x] for x in syn if x in nw2c ]
    if len(set( tuple(sorted(x)) for x in synCodes )) > 2:
        continue
    
    for y in syn:
        synMap[y] = k
        
def getOccCodes(k):
    if k in synMap:
        k = synMap[k]
    
    if k in nw2c:
        return nw2c[k]
    
    return []

def follow(w, dep):
    return [x for x in w.children if x.dep_ == dep]

def isPrepPhrase(w):
    for x in w.children:
        if x.dep_ == 'prep':
            return True
    return False

def enterPrepPhrase(w):
    s1 = follow(w, 'prep')
    
    ret = []
    for x in s1:
        ret += follow(x, 'pobj')
    
    return ret

def expandCompound(w):
    full = str(w)
    for x in w.children:
        if x.dep_ == 'compound':
            return expandCompound(x) + " " + full
    
    return full
    
def vagueExpand(n):
    # just need to know if it's a company or a country
    if str(n) == 'president':
        entityBase = enterPrepPhrase(n)
        print(entityBase)
        
def whatWordsThisCode(c):
    initial = [ x for x in list(w2c.keys()) if 'occ2000-%s' % c in w2c[x] and len(x.split()) == 1 ]
    synonyms = [ k for (k,v) in synMap.items() if v in initial]
    return initial+synonyms

pdepth = 0
def p(s, extrad=0):
    print( '.'*(pdepth+extrad) + s )

def expandVague(n, entities):
    # ambiguous of what?
    ret = []
    for c in n.children:
        if c.dep_ == 'prep':
            for ofWhat in c.children:
                for e in entities:
                    if ofWhat.i in range(e[0],e[1]):
                        ret.append(e[2])
    return ret
    
    
    
    
    
    
    
    
    
    
if "famousDict" not in locals():
    famousDict = {}

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
   
def lookup(name):
    if name in famousDict:
        return famousDict[name]
    
    query = {
        "action":"wbsearchentities",
        "search": name,
        "language":"en",
        "format":"json"
    }
    
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










with open(inFn) as inF:
    rs = DictReader(inF)
    
    stateCounter = Counter()
    unclassifiedCounter = Counter()
    occSpecificCounter = Counter()
    occVagueCounter = Counter()
    
    debug = True
    
    index = 0
    for r in rs:
        index+=1
        if index > 1000:
            break
        if index % 100 == 0:
            print(index)
        
        fS = firstSentence(r['fullBody'])
        if "died" in fS:
            dSplit = fS.split("died")
            beforeDeath = "died".join( dSplit[:-1] )
            afterDeath = dSplit[-1]
        else:
            beforeDeath = fS
            afterDeath = ""
        
        whatHeWas = beforeDeath
        if len(whatHeWas.split(",")) > 1:
            cSplit = whatHeWas.split(",")
            whatHeWas = ",".join( cSplit[1:] )
            
        whatHeWas = re.split( r"(who)|(whose)|,", whatHeWas )[0]
        whw = nlp(whatHeWas.strip())
        
        #whwCount.update( [ str(g[-1]) for g in guess ] )
        
        struct = "None"
        
        if debug:
            pdepth = 0
            p( fS )
            
            pdepth += 1
        
        name = r['name']
        name = name.replace( "Late Edition - Final\n", "" )
        name = name.replace( "Correction Appended\n", "" )
        name = name.replace( "The New York Times on the Web\n", "" )
        name = name.replace( "National Edition\n", "" )
        name = name.strip()
        if len(name) > 0:
            words = lookup(name)
            lookhimup = set()
            for x in words:
                lookhimup.update(getOccCodes(x))
                
            if len(lookhimup) > 0:
                if debug:
                    p("WikiData returns %s which gives OCC %s" % (words, lookhimup))
        
        if len(whw) == 0:
            p("Skipping. No content after trim.")
            stateCounter.update(["zeroLengthSkip"])
            continue
            
        knownWords = ['member', 'merchant','professor','actor','engineer','scholar','songwriter','trustee','fighter']
        vagueWords = ['founder','director','president', 'member']
        kinshipWords = ['mother','father','uncle','aunt','daughter','son','grandson','granddaughter','neice','nephew', 'sister','brother','wife','husband']
        
        # first grab the root. let's see how close this gets us
        s1 = list(whw.sents)[0]
        root = s1.root
        conjs = [ x for x in list(root.children) if x.dep_ == 'conj' ]
        baseNouns = [root]+conjs
        for i,x in enumerate(baseNouns):
            if isPrepPhrase(x) and str(x) == 'one':
                baseNouns[i] = enterPrepPhrase(x)[0]
                
        entities = [ (e.start, e.end, e.text) for e in whw.noun_chunks ]
        
        for n in baseNouns:
            ns = wn.morphy(str(n))
            if ns is None:
                ns = str(n)
            ns = ns.lower()
#==============================================================================
#             if ns in knownWords:
#                 stateCounter.update(["known"])
#                 continue
#==============================================================================
            if ns in vagueWords:
                stateCounter.update(["vague"])
                if debug:
                    p("identified vague word %s"%ns)
                    ev = expandVague(n, entities)
                    if ev:
                        p("expanded to %s (of) %s"%( ns, ev ), 1)
                continue
            if ns in kinshipWords:
                stateCounter.update(["kinship"])
                if debug:
                    p("identified kinship word %s"%ns)
                    ev = expandVague(n, entities)
                    if ev:
                        p("expanded to %s (of) %s"%( ns, ev ), 1)
                continue
            
            occLookup = getOccCodes(ns)
            
            if len(occLookup) > 0:
                if len(occLookup) > 1:
                    stateCounter.update(["vague_occWords"])
                    if debug:
                        p("multiple OCC for %s: %s" % (ns, occLookup))
                    occVagueCounter.update(occLookup)
                else:
                    stateCounter.update(["specific_occWords"])
                    if debug:
                        p("single OCC for %s: %s" % (ns, occLookup))
                    occSpecificCounter.update(occLookup)
                continue
                
            if len(lookhimup) > 0:
                stateCounter.update(["justWikidata"])
            else:
                stateCounter.update(["unclassified"])

            if debug:
                p("no OCC for %s" % ns)
                ev = expandVague(n, entities)
                if ev:
                    p("expanded to %s (of) %s"%( ns, ev ), 1)
            unclassifiedCounter.update([ns])
        
        #print("\n\n\n")
        

#==============================================================================
# Similarity measures
#==============================================================================
        
#==============================================================================
#             maxi = -1
#             maxs = -1
#             for x in knownWords + vagueWords + occWords:
#                 w1 = wn.synsets(str(n))
#                 w2 = wn.synsets(x)
#                 if len(w1) == 0 or len(w2) == 0:
#                     continue
#                 
#                 simComp = [ w1i.path_similarity( w2i ) for w1i in w1 for w2i in w2 ]
#                 simComp = list(filter( lambda x: x is not None, simComp ))
#                 if len(simComp) == 0:
#                     continue
#                 
#                 sim = max(simComp)
#                 
#                 if sim > maxs:
#                     maxi = x
#                     maxs = sim
#                     
#             if maxi != -1:
#                 print("mostSimilar", str(n), maxi, maxs)
#==============================================================================
