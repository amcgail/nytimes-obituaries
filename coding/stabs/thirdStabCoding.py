# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 15:55:27 2017

@author: alec

DOCUMENTATION:
https://spacy.io/usage/linguistic-features#dependency-parse
(visualization)
https://spacy.io/usage/visualizers

"""

import sys
from collections import Counter
from csv import reader
from itertools import chain
from os import path

from nltk import sent_tokenize

from nlp import extractLexical
from occ import extractCodes

sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )

from g import *

if 'nlp' not in locals():
    import spacy
    nlp = spacy.load('en')

inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )

debug = False

notCoded = []
coded = []

confidenceHist = []

csv.field_size_limit(500 * 1024 * 1024)

with open(inFn) as inF:
    rs = reader(inF)
    
    head = rs.next()
    
    n = 0
    for r in rs:
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

if True:
    outCSVfn = path.join( path.dirname(__file__), "thirdStabCoding.csv" )
                    
    with open(outCSVfn, 'w') as outF:
        outCSV = writer(outF)
        outCSV.writerow(["fn","firstSentence", "confidence", "codes"])
        
        for cr in coded:
            outCSV.writerow(cr)
            
    outCSVfn = path.join( path.dirname(__file__), "thirdStabCoding.notCoded.csv" )
                    
    with open(outCSVfn, 'w') as outF:
        outCSV = writer(outF)
        outCSV.writerow(["fn","firstSentence","confidence"])
        
        for cr in notCoded:
            outCSV.writerow(cr)
