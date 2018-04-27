# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# =============================================================================
# Possible next steps:
#     + Create classes as containers for functions
#     + More library classes to the library folder and import them
# =============================================================================



from collections import Counter

from nltk.corpus import wordnet as wn
from spacy.matcher import Matcher

from time import time as now
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
import random

import urllib

basedir = path.join( path.dirname(__file__), '..', ".." )

sys.path.append( path.join( basedir, 'lib' ) )

from lib import *

if 'nlp' not in locals():
    import spacy
    nlp = spacy.load('en')

inFn = path.join( basedir, "data","extracted.all.nice.csv" )

debug = True

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

allResults = []

def getSentences(word):
    for res in allResults:
        words = [x['word'] for x in res['guesses']]
        if word in words:
            yield res['sentence']
            
def getBySubstr(substr):
    for res in allResults:
        if substr in res['sentence']:
            yield res['sentence']


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
        p(lastJ)
        if lastJ < 0:
            splits.append(doc[:j])
        else:
            splits.append(doc[lastJ:j])
        lastJ = j+len(seq)
    splits.append(doc[lastJ:])
    return splits


# these all deal with synonyms (hypernyms and hyponyms)
    

from pptree import *
class synsetNode:

    def __init__(self, s):
        self.hyponyms = [ synsetNode(x) for x in s.hyponyms() ]
        
        self.s = s
        self.word = str(s)

    #def __str__(self):
    #    return self.function
    
    def __str__(self):
        return str(self.s)

# accepts a synset
def printHyponymTree(s):
    print_tree( synsetNode(s), "hyponyms" )
# accepts a synset
def printHyponymTrees(s):
    for ser in s.hypernyms():
        print_tree( synsetNode(ser), "hyponyms" )




def distanceToPerson(s):
    ds = s.hypernym_distances()
    for parent, d in ds:
        if parent == wn.synset('person.n.01'):
            return d
    
    # if it's not even a parent
    return -1

def synonyms(w):
    if '.' in w:
        parts = w.split('.')
        if len( parts ) < 3:
            return []
        
        try:
            int(parts[-1])
        except:
            return []
        
        s = wn.synset(w)
    else:
        ss = wn.synsets(w, pos='n')
    
        if len(ss) == 0:
            return []
        
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
    
    #print(allS)
    
    syns = [x.name() for y in allS for x in y.lemmas()]
    syns = [x for x in syns if '_' not in x]# and x.lower() == x]
    
    return list(set(syns))

     
def getOccCodes(k):
    if k in synMap:
        k = synMap[k]
    
    if k in nw2c:
        return nw2c[k]
    
    return []

def follow(w, dep):
    return [x for x in w.children if x.dep_ == dep]

def followRecursive(ws, deps, depth=0):
    if len(ws) == 0:
        return []
        
    if type(deps) != list:
        deps = [deps]
    if type(ws) != list:
        ws = [ws]
        
    def expandSpans(w):
        if hasattr(w, "root"):
            return w.root
        return w
    ws = list(map(expandSpans, ws))
    
    nextStep = list(chain.from_iterable( follow(w,dep) for dep in deps for w in ws )) 
    return followRecursive(nextStep, deps, depth+1) + ws

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
        p(entityBase)
        
def whatWordsThisCode(c):
    initial = [ x for x in list(w2c.keys()) if 'occ2000-%s' % c in w2c[x] and len(x.split()) == 1 ]
    synonyms = [ k for (k,v) in synMap.items() if v in initial]
    return initial+synonyms
    
def getContainingEntity(w):
    entities = [ (e.start, e.end, e.text) for e in w.doc.noun_chunks ]
    for e in entities:
        if w.i in range(e[0],e[1]):
            return e[2]
    return None

pdepth = 0
def p(*s, extrad=0):
    global poutf
    s = " ".join( str(ss) for ss in s )
    print( '.'*(pdepth+extrad) + str(s), file=poutf )

def expandVague(n, entities):
    # ambiguous of what?
    ws = []
    for c in n.children:
        if c.dep_ == 'prep':
            for ofWhat in c.children:
                ws.append(ofWhat)

    ws = followRecursive(ws, 'conj')
    ws = map(getContainingEntity, ws)
    ws = filter(lambda x: x is not None, ws)
    return list(ws)


def nounIdentify(n):
    #knownWords = ['member', 'merchant','professor','actor','engineer','scholar','songwriter','trustee','fighter']
    vagueWords = ['founder','director','president', 'member']
    kinshipWords = ['mother','father','uncle','aunt','daughter','son','grandson','granddaughter','neice','nephew', 'sister','brother','wife','husband']

    entities = [ (e.start, e.end, e.text) for e in n.doc.noun_chunks ]
    
    ret = {
        "word": str(n),
        "state":"unclassified",
        "preps":[],
        'occ':[]
    }

    ns = wn.morphy(str(n))
    if ns is None:
        ns = str(n)
    ns = ns.lower()
#==============================================================================
#             if ns in knownWords:
#                 stateCounter.update(["known"])
#                 continue
#==============================================================================
        
    ev = expandVague(n, entities)
    if ev and debug:
        p("expanded to %s (of) %s"%( ns, ev ), extrad=1)
        
    ret['preps'] = ev    
    
    if ns in vagueWords:
        if debug:
            p("identified vague word %s"%ns)
            
        ret['state'] = 'vague'
        return ret
    
    if ns in kinshipWords:
        if debug:
            p("identified kinship word %s"%ns)

        ret['state'] = 'kinship'
        return ret
    
    occLookup = getOccCodes(ns)
    ret['occ'] = occLookup
    
    if len(occLookup) > 0:
        if len(occLookup) > 1:
            if debug:
                p("multiple OCC for %s: %s" % (ns, occLookup))
                
            ret['state'] = "vague_occWords"
        else:
            if debug:
                p("single OCC for %s: %s" % (ns, occLookup))
                
            ret['state'] = 'specific_occWords'
            
        return ret

    if debug:
        p("no OCC for %s" % ns)
        
    return ret

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
    
    print(r['results']['bindings'])
    return
   

if "famousDict" not in locals():
    famousDict = {}
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


def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]








with open('out.txt', 'w') as poutf:

    pattern1 = [{'POS':'VERB', 'OP':'!'}, {'POS': 'CCONJ'}, {'POS': 'DET', 'OP':'?'}, {'POS': 'ADV', 'OP': "*"}, {'POS': 'ADJ', 'OP': "*"}, {'POS': 'NOUN', 'OP': "+"}]
    pattern2 = [{'POS':'VERB', 'OP':'!'}, {'POS': 'DET'}, {'POS': 'ADV', 'OP': "*"}, {'POS': 'ADJ', 'OP': "*"}, {'POS': 'NOUN', 'OP': "+"}]
    matcher = Matcher(nlp.vocab)
    matcher.add('adjNoun', None, pattern1) # add pattern
    matcher.add('adjNoun', None, pattern2) # add pattern
    
    skipped = 0
    #whwCount = Counter()
    
    sCount = Counter()
    
    nw2c = {}
    
    # filter out non-OCC2000 codes

    for k,codes in w2c.items():
        if len(k.split()) != 1:
            continue
        
        def fCode(c):
            try:
                n = int(c.lower().split("occ2000-")[1])
            except ValueError:
                return False
                
            if n >= 620 and n < 900:
                return False
            return True
        
        nc = [c for c in codes if 'occ2000' in c]
        nc = list(filter(fCode, nc))
        if len(nc) == 0:
            continue
        
        nw2c[k] = nc
    
    # my hand-coding
    
    nw2c['professor'] = ['occ2000-220']
    #w2c['scholar'] = ['occ2000-']
    nw2c['writer'] = ['occ2000-285']
    nw2c['photographer'] = ['occ2000-291']
    nw2c['filmmaker'] = ['occ2000-271']
    nw2c['football_player'] = ['occ2000-276']
    nw2c['composer'] = ['occ2000-285'] # is this true!?
    nw2c['virtuoso'] = ['occ2000-275']
    nw2c['politician.n.01'] = ['occ2000-003']
    nw2c['scholar'] = ['occ2000-186'] # not certain!    
    nw2c['politician.n.02'] = ['political proponent'] # actually a specific definition. interesting
    
    #all except agent.n.02
    for x in wn.synset('representative.n.01').hypernyms():
        if x != wn.synset('agent.n.02'):
            nw2c[x.name()] = ['occ2000-003']
            
    nw2c['musician.n.01'] = nw2c['musician.n.02'] = ['occ2000-275']
    
    
    # add alternative words, whose codes are themselves
    altClass = ["volunteer", "thief", "defender", "champion", "veteran"
        "leader",
        "philanthropist",
        "benefactor",
        "widow"]
    for aC in altClass:
        nw2c[aC] = [aC]
        
    nw2c['epidemiologist'] = ['occ2000-165']
    nw2c['painter'] = ['occ2000-260']
    nw2c['sculptor'] = ['occ2000-260']
    nw2c['player.n.01'] = ['occ2000-276']
            
    # now expand this vocabulary with synonyms:
    synMap = {}
    
    for k,v in nw2c.items():
        syn = synonyms(k)
        
        #synCodes = [ nw2c[x] for x in syn if x in nw2c ]
        #if len(set( tuple(sorted(x)) for x in synCodes )) > 2:
        #    continue
        
        for y in syn:
            synMap[y] = k
        
        
        
        
        
        
        
        
        
        
    

    
    
    
    
    
    
    

    
    
    
    
    
    
    
    rows = []
    with open(inFn) as inF:
        rs = DictReader(inF)
        rows = map( dict, rs )
        rows = list(rows)
    
    random.shuffle(rows)
    rows = rows[:1500]
    
    stateCounter = Counter()
    specificCounters = {}
    
    timeArray = []
    
    index = 0
    for index, r in enumerate(rows):
        pdepth = 0
        
        if index % 100 == 0:
            print(index)
        
        fS = firstSentence(r['fullBody'])
        
        # parse using SpaCy. how long does it take?
        t1 = now()
        whw = nlp(fS.strip())
        t2 = now()
        timeArray.append( t2 - t1 )
        
        fS = fS.replace( "Late Edition - Final\n", "" )
        fS = fS.replace( "Correction Appended\n", "" )
        fS = fS.replace( "The New York Times on the Web\n", "" )
        fS = fS.replace( "National Edition\n", "" )
        
        # for those "LONDON --"s
        fS = re.sub(r'^[A-Z\s\(\)]*(--)\s+', '', fS)
    
        #OMG
        # this simply gets rid of a date at the beginning of the line.
        monthDateRe = r"^(\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?(\d{1,2}\D?)?\D?((19[7-9]\d|20\d{2})|\d{2})\.?\s*"
        fS = re.sub(monthDateRe, '', fS)
    
        if len(whw) == 0:
            p("Skipping. No content after trim.")
            stateCounter.update(["zeroLengthSkip"])
            continue
        
        #whwCount.update( [ str(g[-1]) for g in guess ] )
        
        struct = "None"
        
        if debug:
            p()
            p( fS )
            
            pdepth += 1
        
        name = next(whw.noun_chunks)
        nameS = str(name)
        
        if len(nameS) > 0:
            words = lookup(nameS)
            lookhimup = set()
            for x in words:
                lookhimup.update(getOccCodes(x))
                
            if len(lookhimup) > 0:
                if debug:
                    p("WikiData returns %s which gives OCC %s" % (words, lookhimup))
                    
        if debug:
            p("Extracted name: %s" % name)
            
            
        # extract information from the title
        dieWords = ['dies','die','dead']
        t = r['title']
        t = t.split("\n")[-1] # gets rid of those gnarly prefixes
        ts = [x.strip() for x in re.split(r'[;,]|--', t)]
        ts = ts[1:] #the name is always the first one
            
        #print("")
        #print(nameS)
        #print(ts)
        for tp in ts:
            
            # this was dumb. the name is the first entry. always
            #
            # cutoff = max(len(tp),len(nameS)) / 2.
            # if levenshteinDistance( tp.lower(), nameS.lower() ) < cutoff:
            #     continue
            #
            
            tpW = [ x.lower() for x in word_tokenize(tp) ]
            hasDeathWord = False
            for dW in dieWords:
                if dW in tpW:
                    hasDeathWord = True
            if hasDeathWord:
                continue
            
            # if it's a number, continue
            try:
                int(tp)
                continue
            except:
                pass
            
            print(tp)
                
        
        didSomething = False
        
        guesses = []
        
        # Alec McGail, scientist and genius, died today.
        nameChildren = list( name.root.children )
        apposHooks = list(filter( lambda x: x.dep_ == 'appos', nameChildren ))
        
        if len( apposHooks ) > 0:
            didSomething = True
            
            # follow conjs exclusively
            baseNouns = followRecursive( apposHooks, 'conj' )
            for i,x in enumerate(baseNouns):
                if isPrepPhrase(x) and str(x) == 'one':
                    baseNouns[i] = enterPrepPhrase(x)[0]
            
            for n in baseNouns:
                result = nounIdentify(n)
                
                stateCounter.update([ result['state'] ])
                
                if result['state'] not in specificCounters:
                    specificCounters[result['state']] = Counter()
                #specificCounters[result['state']].update(result['occ'])
                specificCounters[result['state']].update([result['word']])
                
                guesses.append(result)
    
        allResults.append({
            "sentence": fS,
            "guesses": guesses
        })
    
        # Alec McGail, who ..., died today.
        relcls = list(filter( lambda x: x.dep_ == 'relcl', nameChildren ))
    
        if len(relcls) > 0:
            pdepth += 1
            
        for relcl in relcls:
            # need to follow advcl and conj
            goDeep = followRecursive(relcl, ['advcl', 'conj'] )
            be = ['was','became']
            for v in goDeep:
                # as _
                followPreps = followRecursive( v, ['relcl','prep','pobj'] )
                asWhat = [x for x in followPreps if next(x.ancestors).text == 'as' and x.pos_ == 'pobj']
    
                if debug and len(asWhat):
                    p('whoAs', asWhat)
                    
                if len(asWhat):
                    didSomething = True
    
                
                # who was a scientist and inventor
                if v.pos_ == 'VERB':
                    if v.text in be:
                        for vc in v.children:                                
                            if vc.dep_ != 'attr':
                                continue
                                                        
                            if debug:
                                p('Expanded be verb', vc, vc.dep_)
    
                            #guesses.append(result)
                            didSomething = True
    
        finalGuess = []
        for guess in guesses:
            if len(guess['occ']) != 1:
                continue
            finalGuess.append(guess['occ'][0])
        
        p("finalGuess", finalGuess)
    
        if True:
            moreGuesses = []
            # more stupid guesses...
            # literally expand every noun
            
            for w in whw:
                if w.pos_ != 'NOUN':
                    continue
                guess = nounIdentify(w)
                moreGuesses.append(guess)        
        
            stupidFinalGuess = []
            for guess in moreGuesses:
                stupidFinalGuess += guess['occ']
            
            p("stupidFinalGuess", stupidFinalGuess)
            
            if set(stupidFinalGuess) != set(finalGuess):
                p("And they're different!", extrad=1)
                
    
        if not didSomething:
            if len(lookhimup) > 0:
                stateCounter.update(["justWikidata"])
            else:
                if debug:
                    p("Skipping. Strange grammatical construction.")
                stateCounter.update(["strangeGrammar"])
                
        if False:        
            allResults.append({
                "sentence": fS,
                "guesses": guesses,
                "finalGuess": finalGuess
            })
        
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
    
    #import cProfile
    #cProfile.run("goParse()", "parsingPerformanceStats")
    #goParse()
    
    
#let's see if we can go about GROUPING these unclassified words
    
#just take the first one
    
hyponymSets = {}
    
for w1 in specificCounters['unclassified']:
    ss = wn.synsets(w1)
    if len(ss) == 0:
        print(w1, "has no definition")
        continue

    s = ss[0]
    hyp = s.hyponyms()
    
    myhyp = []
    
    for w2 in specificCounters['unclassified']:
        if w1 == w2:
            continue
        
        ss2 = wn.synsets(w2)
        if any( x in hyp for x in ss2 ):
            myhyp.append( w2 )
    
    hyponymSets[w1] = myhyp
    

# make a simple count of OCC codes
    
OCCsingle = Counter()
OCCmultiple = Counter()    
OCCcomb = Counter()    

for x in allResults:
    g = list(chain.from_iterable( y['occ'] for y in x['guesses'] ))
    if len(g) == 1:
        OCCsingle.update(g)

# should it be fractional?
for x in allResults:
    g = list(chain.from_iterable( y['occ'] for y in x['guesses'] ))
    for y in g:
        OCCmultiple[y] += 1./len(g)

# or tuples?
for x in allResults:
    g = list(set(chain.from_iterable( y['occ'] for y in x['guesses'] )))
    g = tuple(sorted(g))
    OCCcomb[g] += 1
    
OCCgraph = Counter()
# we could build a graph
for x in allResults:
    g = list(set(chain.from_iterable( y['occ'] for y in x['guesses'] )))
    for x1 in g:
        for x2 in g:
            if x1 >= x2:
                continue
            OCCgraph[(x1,x2)] += 1