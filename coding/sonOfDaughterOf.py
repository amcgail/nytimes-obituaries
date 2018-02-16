# -*- coding: utf-8 -*-

import csv
from csv import reader
from csv import QUOTE_MINIMAL
from nltk import sent_tokenize, word_tokenize
from os import path
from collections import Counter
import numpy as np
import re
import sys
from itertools import chain

sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )

from lib import *

if 'nlp' not in locals():
    import spacy
    nlp = spacy.load('en')

inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )

debug = False

notCoded = []
coded = []

confidenceHist = []

csv.field_size_limit(500 * 1024 * 1024)

familial = [
    "daughter of",
    "son of",
    "wife of",
    "mother of",
    "father of",
    "husband of",
    "fiance of"
]

famC = 0
total = 0

with open(inFn) as inF:
    rs = csv.DictReader(inF)
    
    n = 1
    for r in rs:
        #if n > 10000:
        #    break
    
        total += 1
        
        if n%100 == 0:
            break
            print( n )
            
        sentences = sent_tokenize(r['fullBody'])
        
        if len(sentences) < 2:
            print("skipping(tooFewSentences)", r['fName'])
            continue
        
        firstSentence = sentences[0].strip()
        firstSentence = " ".join( firstSentence.split() )

        fam = False        
        for x in familial:
            if x in firstSentence:#r['first500']:
                fam = True
            
        if not fam:
            continue
        
        print( r['title'] )
        print( r['first500'] )
        print( "\n\n\n" )
        n += 1
        famC += 1