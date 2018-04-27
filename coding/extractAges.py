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

basedir = path.join( path.dirname(__file__), '..' )

sys.path.append( path.join( basedir, 'lib' ) )

from lib import *

if 'nlp' not in locals():
    import spacy
    nlp = spacy.load('en')

inFn = path.join( basedir, "data","extracted.all.nice.csv" )

debug = True

notCoded = []
coded = []

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
    
    
    

confidenceHist = []

csv.field_size_limit(500 * 1024 * 1024)

success = 0
fail = 0

with open(inFn) as inF:
    rs = DictReader(inF)
    
    stateCounter = Counter()
    specificCounters = {}
    
    ageCounter = Counter()    
    
    index = 0
    for r in rs:
        pdepth = 0        
        
        index+=1
        if index < 1200:
            continue
        
        if index > 3200:
            break
        if index % 100 == 0:
            print(index)
        
        #print( firstSentence(r['fullBody']) )        
        
        name = next( nlp(r['fullBody']).sents ).noun_chunks
        name = next(name)
        lastName = name.text.split()[-1]

        rgxs = [
            r"(?:Mr\.?|Mrs\.?)\s*%s\s*was\s*([0-9]{1,3})(?:\s*years\s*old)?" % lastName,
            r"(?:She|He)\s*was\s*([0-9]{1,3})(?:\s*years\s*old)?",
            r"died.*at\s+the\s+age\s+of\s+([0-9]{1,3})",
            r"was\s*([0-9]{1,3})\s*years\s*old",
            r"was\s*([0-9]{1,3})",
            r"([0-9]{1,3})\s*years\s*old",
            r"was\s*believed\s*to\s*be([^,\.]*)",
            r"was\s*in\s*(?:his|her)\s*([^,\.]*)",
            r"([0-9]{1,3})",
        ]
        
        sents = list(nlp(r['fullBody']).sents)
        
        # simply look for that sentence.
        for rgx in rgxs:
            for s in sents:
                fAge = re.findall( rgx, s.text )
                if len(fAge):
                    break
                
            if len(fAge):
                    break
            
        if len(fAge) != 1:
            print( r['fullBody'] )
            print("lastName",lastName)
            print("")
            fail += 1
        else:
            fail = False
            for x in fAge:
                try:
                    xi = int(x)
                    if xi > 120 or xi < 15:
                        print( r['fullBody'] )
                        print("lastName",lastName)
                        print("fAge",fAge)
                        print("")
                        fail = True
                        break
                except ValueError:
                    pass
            if fail:                
                fail += 1
            else:
                success += 1
            ageCounter.update(fAge)
        