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

pattern1 = [{'POS': 'CONJ'}, {'POS': 'DET', 'OP':'?'}, {'POS': 'ADV', 'OP': "*"}, {'POS': 'ADJ', 'OP': "*"}, {'POS': 'NOUN', 'OP': "+"}]
pattern2 = [{'POS': 'DET'}, {'POS': 'ADV', 'OP': "*"}, {'POS': 'ADJ', 'OP': "*"}, {'POS': 'NOUN', 'OP': "+"}]
matcher = Matcher(nlp.vocab)
matcher.add('adjNoun', None, pattern1) # add pattern
matcher.add('adjNoun', None, pattern2) # add pattern

skipped = 0
whwCount = Counter()

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
        name = cSplit[0]
        whatHeWas = ",".join( cSplit[1:] )
        
        whatHeWas = re.split( r"(who)|(whose)|,", whatHeWas )[0]
        whw = whatHeWas
        whw = nlp(whw.strip())
        
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
        
        
        #for w in whw:
        #    print( w, w.pos_ )
        #print(whw.root, whatHeWas)
        #print(whatHeWas)

        matches = matcher(whw)
        guess = [ whw[s:e] for i,s,e in matches if not (s>0 and whw[s].pos_ == "DET") ]
        #print(guess)
        
        whwCount.update( [ str(g[-1]) for g in guess ] )

        continue
    
        ambiguous = ["president","trustee","founder","chairman","professor","pioneer"]
    
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
                
                
    
        state="S"
        
        what = ""
        
        adjectives = []
        
        for w in word_tokenize( whatHeWas.strip() ):
            if state=="S":
                if w in ["a","an","the"]:
                    state="WHAT"
                    
            elif state=="WHAT":
                #if w in ["in"]
                
                what += " "+ w
        
        #sParse = nlp(afterDeath)
        
        continue
        
        #if n > 10000:
        #    break
        n += 1
        if n%100 == 0:
            #break
            print( n )
        
        fn = r[head.index('fName')]
        body = r[head.index('fullBody')]
        
        if len( body.strip() ) < 10:
            print("skipping(noBody)", fn)
            continue
        
        first500 = body[:500]
        name = r[head.index('name')]
        nameParts = re.split("[\s\.]", name)
        nameParts = [x.lower() for x in nameParts]
        nameParts = [x for x in nameParts if len(x) > 3]
        
        namePartSkips = ["dead"]
        nameParts = [x for x in nameParts if x not in namePartSkips]
        
        sentences = sent_tokenize(body)
        
        if len(sentences) < 2:
            print("skipping(tooFewSentences)", fn)
            continue
        
        firstSentence = sentences[0].strip()
        firstSentence = " ".join( firstSentence.split() )
        
        reStartStrip = [
            "[A-Z\s]+,.{1,30}[0-9]+\s*", # city and date
            "\(AP\) -\s*", # AP tag
        ]        
        
        for patt in reStartStrip:
            findTag = re.match(patt, firstSentence)
            if findTag:
                firstSentence = firstSentence[findTag.end():]

        if "," not in firstSentence:
            firstSentence += " " + " ".join( sentences[1].strip().split() )
        
        commaSplit = firstSentence.split(",")            
        if len(commaSplit) == 1:
            continue
        
        name = commaSplit[0]
        for lastThing, c in enumerate(commaSplit):
            if "died" in c.lower():
                break
            
        clause = ",".join( commaSplit[1:lastThing] )
        
        firstSentence = clause
        
        wasDid = extractLexical( body, name )
        wasDidC = []
        for x in wasDid['did']:
            wasDidC += extractCodes( x )
        for x in wasDid['was']:
            wasDidC += extractCodes( x )
        wasDidC = Counter(wasDidC)
        
        fsC = Counter( extractCodes( firstSentence ) )
        f500C = Counter( extractCodes( first500 ) )
        bodyC = Counter( extractCodes( body ) )
        
        weightedC = {}
        w = {}
        w['did'] = 5
        w['fS'] = min( 1, 6*10./len( firstSentence ) ) if len( firstSentence )>0 else 1
        w['f500'] = 0.5 * 6*10./500
        w['body'] = min( 0.1, 0.1 * 6*10./len( body ) ) if len( body )>0 else 1
        
        #print w
        for x in set( fsC.keys() + f500C.keys() + bodyC.keys() ):
            weightedC[x] = wasDidC[x] *w['did'] + fsC[x]*w['fS'] + f500C[x]*w['f500'] + bodyC[x]*w['body']
        
        confidence = max(weightedC.values()) if len(weightedC) > 0 else -1
        
        # print print r[head.index('fName')]
        rankedC = sorted( weightedC.items(), key=lambda x: -x[1] )
        topC = rankedC[:3]
        topC = [list(x) for x in topC]
        
        confidenceHist.append( confidence )
        
        if len(topC) > 0:
            #print( firstSentence, topC )
            coded.append([r[head.index('fName')], firstSentence, confidence] + list(chain( *topC )))
        else:
            notCoded.append([r[head.index('fName')], firstSentence])