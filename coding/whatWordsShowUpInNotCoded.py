# -*- coding: utf-8 -*-

import sys
from collections import Counter
from os import path

from nlp import extractLexical, extractFirstSentence

sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )
from g import *

# get docs which weren't coded
notCodedfn = path.join( path.dirname(__file__), "secondStabCoding.notCoded.csv" )
with open(notCodedfn) as notCodedf:
    notCoded = list(DictReader(notCodedf))
notCoded = [x['fn'] for x in notCoded]



inFn = path.join( path.dirname(__file__), "..", "data","extracted.nice.csv" )

fsC = Counter()
f500C = Counter()
bodyC = Counter()
nC = Counter()
vC = Counter()

globalC = Counter()

examples = {}

with open(inFn) as inF:
    rs = DictReader(inF)
    
    n = 0
    for r in rs:
        fn = r['fName']
        if fn not in notCoded:
            continue
        
        n += 1
        if n % 20 == 0:
            print(n)

        body = r['fullBody']
        first500 = body[:500]
        
        firstSentence = extractFirstSentence(body)
        
        name = r['name']
        nameParts = re.split("[\s\.]", name)
        nameParts = [x.lower() for x in nameParts]
        nameParts = [x for x in nameParts if len(x) > 3]
        
        namePartSkips = ["dead"]
        nameParts = [x for x in nameParts if x not in namePartSkips]
        
        wereDid = extractLexical( body, " ".join(r['name']) )
        nv = extractNV( body )
        
        globalC += Counter( set( word_tokenize( body ) ) )
        
        def larr(arr):
            return [x.lower() for x in arr]
        
        fsC += Counter( larr( word_tokenize( firstSentence ) ) )
        f500C += Counter( larr( word_tokenize( first500 ) ) )
        bodyC += Counter( larr( word_tokenize( body ) ) )
        nC += Counter( larr( nv["N"] ) )
        vC += Counter( larr( nv["V"] ) )

        sents = sent_tokenize(body)
        sents = [word_tokenize(s) for s in sents]
        
        for k in bodyC:
            if k not in examples:
                examples[k] = []
            if len(examples[k]) >= 3:
                continue
            
            for s in sents:
                if k in s:
                    examples[k].append( " ".join(s) )
                    
                    if len(examples[k]) >= 3:
                        break

import os
outDir = path.join( path.dirname(__file__), "notCoded_words" )
if not path.exists(outDir):
    os.mkdir(outDir)

vsToOutput = ["fsC","f500C","bodyC","nC","vC"]
for v in vsToOutput:        
    outFn = path.join( outDir,"%s.csv" % v )
    
    vv = locals()[v]
    
    # to remove some abnormalities caused by the truncation in first500
    vv = {k:v for k,v in vv.items() if globalC[k] > 0}
    
    # to remove uninteresting words. those which occur in more than half of documents, or 5 or less docs
    vv = {k:v for k,v in vv.items() if globalC[k] > 5 and float(globalC[k])/n < 0.5}
    
    with open(outFn, 'w') as outFn:
        outC = writer(outFn)
        outC.writerow( ["word","count","docCount"] )
        for word,c in sorted( vv.items(), key=lambda x: float(x[1])/globalC[x[0]], reverse=True ):
            ex = []
            if word in examples:
                ex = examples[word]
            outC.writerow([word, c, globalC[word]] + ex)
