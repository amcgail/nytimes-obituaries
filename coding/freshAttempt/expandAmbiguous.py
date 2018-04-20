# -*- coding: utf-8 -*-

from collections import Counter

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

sCount = Counter()

with open(inFn) as inF:
    rs = DictReader(inF)
    
    head = next(rs)
    
    n = 0
    for r in rs:
        n+=1
        if n > 10000:
            break
        if n % 100 == 0:
            print(n)
        
        fS = firstSentence(r['fullBody'])
        dSplit = fS.split("died")
        beforeDeath = "died".join( dSplit[:-1] )
        afterDeath = dSplit[-1]
        
        cSplit = beforeDeath.split(",")
        whatHeWas = ",".join( cSplit[1:] )
        whatHeWas = re.split( r"(who)|(whose)|,", whatHeWas )[0]
        whw = whatHeWas
        whw = nlp(whw.strip())
        
        print(whw)
        
        if len(whw) == 0:
            #print("skipping",fS)
            skipped += 1
            continue

        if str(whw[0]) not in ["a", "an", "the"]:
            #print("skipping", fS)
            skipped += 1
            continue
        
        #entities = [ (e.start, e.end, e.text) for e in whw.ents ]
        entities = [ (e.start, e.end, e.text) for e in whw.noun_chunks ]

        matches = matcher(whw)
        guess = [ whw[s:e] for i,s,e in matches ]

        ambiguous = ["president","trustee","founder","chairman","professor","pioneer"]
    
        print(len(matches))
    
        for i,s,e in matches:
            p = whw[e-1]
            for c in p.children:
                if c.dep_ == 'prep':
                    for ofWhat in c.children:
                        for e in entities:
                            if ofWhat.i in range(e[0],e[1]):
                                print("%sOf:"%str(p), e[2])    
        continue    
    
        for amb in ambiguous:
            for i,s,e in matches:
                try:
                    pS = [x.text for x in whw[s:e]].index(amb)
                except ValueError:
                    continue
                
                p = whw[s+pS]
                for c in p.children:
                    if c.dep_ == 'prep':
                        for ofWhat in c.children:
                            for e in entities:
                                if ofWhat.i in range(e[0],e[1]):
                                    print("%sOf:"%amb, e[2])
        
        #sParse = nlp(afterDeath)
        
success = 0
fail = 0
for nounGuess in whwCount:
    if str(nounGuess).lower() in w2c:
        #print( str(nounGuess), w2c[str(nounGuess).lower()] )
        success += 1
    else:
        print( str(nounGuess) )
        fail += 1
        
    #print( success, fail )