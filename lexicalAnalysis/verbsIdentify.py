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
from os import path
basedir = path.join( path.dirname(__file__), '..')
sys.path.append( path.join( basedir, 'lib' ) )
import occ, nlp
import re

from csv import writer

whatAnyoneDid = {}
whatAnyoneWas = {}

mycoder = occ.Coder()
mycoder.loadDocs(100)

debug = True

for doc in mycoder.docs:
    if debug:
        print("processing ", doc.nameS)
    nameParts = re.split("[\s\.]", doc.nameS)
    nameParts = [x.lower() for x in nameParts]
    nameParts = [x for x in nameParts if len(x) > 3]

    namePartSkips = ["dead"]
    nameParts = [x for x in nameParts if x not in namePartSkips]

    # print("testing for ", nameParts)
    #
    # print("--NEW--")
    #
    # whatHeWas = set()
    # whatHeDid = set()
    # for sent in doc.spacy.sents:
    #     for chunk in sent.noun_chunks:
    #         itWasHim = False
    #         whatItWas = None
    #         for np in nameParts:
    #             if np in str(chunk).lower():
    #                 itWasHim = True
    #
    #         if not itWasHim:
    #             continue
    #
    #         whw = nlp.follow(chunk.root, "-nsubj")
    #         whw = nlp.follow(whw, "attr")
    #         whw += nlp.follow(whw, "conj")
    #
    #         whw = list(filter(lambda x: x.pos_ == 'NOUN', whw))
    #
    #         whd = nlp.follow(chunk.root, ["-nsubj"])
    #         whd += nlp.follow(whd, "conj")
    #
    #         whd = list(filter(lambda x: x.pos_ == 'VERB', whd))
    #
    #         if len(whw) or len(whd):
    #             print("sent:", sent)
    #             whatHeWas.update(whw)
    #             whatHeDid.update(whd)
    #
    # print("was:", whatHeWas)
    # print("did:", whatHeDid)

    whatHeDid = set()
    whatHeWas = set()

    print("--OLD--")

    #print sentences
    for sent in doc.spacy.sents:

        verbGroup = {}

        for chunk in sent.noun_chunks:
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
                    whatAnyoneWas[whatItWas]['examples'].append(" ".join( str(sent).split() ))
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
                            whatAnyoneDid[wD]['examples'].append(" ".join( str(sent).split() ))

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