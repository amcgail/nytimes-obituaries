# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 15:55:27 2017

@author: alec

DOCUMENTATION:
https://spacy.io/usage/linguistic-features#dependency-parse
(visualization)
https://spacy.io/usage/visualizers

"""

from csv import reader, writer

import re

if 'nlp' not in locals():
    import spacy
    from nltk import sent_tokenize
    nlp = spacy.load('en')

inFn = "/home/alec/projects/nytimes-obituaries/data/extracted.nice.csv"
#outFn = "/home/alec/data projects/NYTIMESobituaries/extracted.noBody.nice.abberations.csv"

whatAnyoneDid = {}
whatAnyoneWas = {}

import sexmachine.detector as gender
detector = gender.Detector()

debug = False

from collections import Counter

c = Counter()

with open(inFn) as inF:
    rs = reader(inF)
    
    head = rs.next()
    
    n = 0
    for r in rs:
        if n > 10000:
            break
        if n%100 == 0:
            print(n)
        n += 1
        
        body = r[head.index('fullBody')]
        name = r[head.index('name')]
    
        nameParts = re.split("[\s\.]", name)
        nameParts = [x.lower() for x in nameParts]
        nameParts = [x for x in nameParts if len(x) > 3]
        
        namePartSkips = ["dead"]
        nameParts = [x for x in nameParts if x not in namePartSkips]
        
        if debug:
            print(nameParts)
        
        if debug:
            print("Processing %s" % name)
        whatHeDid = set()
        whatHeWas = set()
        
        sentences = sent_tokenize(body)
        #print sentences
        for s in sentences:
            s = unicode(s)
            
            #print "-------------"
            if debug:
                print(" ".join( s.split() ))
            doc = nlp(s)
            
            verbGroup = {}
            
            for chunk in doc.noun_chunks:
                fullInfo = [chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text]
                if chunk.root.dep_ in ['nsubj', 'dobj', 'attr']:
                    idx = chunk.root.head.idx
                    if idx not in verbGroup:
                        verbGroup[idx] = []
                    verbGroup[idx].append(fullInfo)
                    
            #print verbGroup

            for vi in verbGroup:
                if "attr" in [x[-2] for x in verbGroup[vi]]:
                    itWasHim = False
                    whatItWas = None
                    for info in verbGroup[vi]:
                        for np in nameParts:
                            if np in info[0].lower():
                                itWasHim = True
                        if info[-2] == 'attr':
                            whatItWas = info[0]
                            whatItWas = " ".join( whatItWas.split() )
                    if itWasHim:
                        whatHeWas.add( whatItWas )
                        
                        if whatItWas not in whatAnyoneWas:
                            whatAnyoneWas[whatItWas] = {"count":0, "examples": []}
                        whatAnyoneWas[whatItWas]['count'] += 1
                        whatAnyoneWas[whatItWas]['examples'].append(" ".join( s.split() ))
                else:
                    for info in verbGroup[vi]:
                        for np in nameParts:
                            if np in info[0].lower():
                                wD = info[-1]
                                wD = " ".join( wD.split() )
                                whatHeDid.add( wD )
                                
                                if wD not in whatAnyoneDid:
                                    whatAnyoneDid[wD] = {"count":0, "examples": []}
                                whatAnyoneDid[wD]['count'] += 1
                                whatAnyoneDid[wD]['examples'].append(" ".join( s.split() ))
             
        if debug:
            print("heDid:",whatHeDid)
            print("heWas:",whatHeWas)

import random
      
with open('whatAnyoneWas.csv', 'w') as csvF:
    w = writer(csvF)
    w.writerow(["what","count","examples"])
    for word in whatAnyoneWas:
        samp = whatAnyoneWas[word]['examples']
        samp = random.sample(samp, min(len(samp), 5))
        samp = "||".join(samp)
        
        w.writerow([word,whatAnyoneWas[word]['count'],samp])
        
with open('whatAnyoneDid.csv', 'w') as csvF:
    w = writer(csvF)
    w.writerow(["what","count","examples"])
    for word in whatAnyoneDid:
        samp = whatAnyoneDid[word]['examples']
        samp = random.sample(samp, min(len(samp), 5))
        samp = "||".join(samp)
        
        w.writerow([word,whatAnyoneDid[word]['count'],samp])