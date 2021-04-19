# -*- coding: utf-8 -*-

import sys
from os import path
from csv import reader
import re
from nltk import sent_tokenize

sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )

inFn = path.join( path.dirname(__file__), "..", "data","extracted.nice.csv" )

from g import *

with open(inFn) as inF:
    rs = reader(inF)
    
    head = rs.next()
    
    n = 0
    for r in rs:
        # if n > 1000:
        #     break
        n += 1
        if n%10 == 0:
            break
            print(n)
            
        body = r[head.index('fullBody')]
        first500 = body[:500]
        name = r[head.index('name')]
        nameParts = re.split("[\s\.]", name)
        nameParts = [x.lower() for x in nameParts]
        nameParts = [x for x in nameParts if len(x) > 3]

        for s in sent_tokenize(doc):
    
            doc = nlp(unicode(s))
            
            verbGroup = {}
            
            for chunk in doc.noun_chunks:
                fullInfo = [chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text]
                #print fullInfo
                continue
                if chunk.root.dep_ in ['nsubj', 'dobj', 'attr']:
                    idx = chunk.root.head.idx
                    if idx not in verbGroup:
                        verbGroup[idx] = []
                    verbGroup[idx].append(fullInfo)
            
            print(s)
            print([to_nltk_tree(sent.root).pretty_print() for sent in doc.sents])
