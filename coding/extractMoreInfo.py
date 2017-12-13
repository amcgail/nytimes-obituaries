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

import wikipedia
from wikipedia import PageError, DisambiguationError

c = Counter()

def scap(s):
    return " ".join( w[0].upper() + w[1:].lower() for w in s.split() )

skipped = 0
hit = 0
disambig = 0

with open(inFn) as inF:
    rs = reader(inF)
    
    head = rs.next()
    
    n = 0
    for r in rs:
        if n > 1000:
            break
        if n%100 == 0:
            print n
        n += 1
        
        body = r[head.index('fullBody')]
        name = r[head.index('name')]

        #print name
        namePartSkips = ["dead", "dies", "is", "of", "killed"]

        nsplit = name.split()

        # finds their first name
        for firstNamei, firstName in enumerate(nsplit):
            if "." in firstName:
                continue
            break
        
        firstName = scap( firstName )
        gender = detector.get_gender(firstName)
        c.update( [gender] )
        
        lastName = nsplit[firstNamei+1:]
        if len(lastName) > 0:
            for endLNi, word in enumerate(lastName):
                #print endLNi, word
                if word.lower() in namePartSkips:
                    endLNi -= 1
                    break
            lastName = lastName[:endLNi+1]
        lastName = scap( " ".join( lastName ) )
        
        fullName = " ".join([firstName,lastName])
        #print fullName
        if False:
            try:
                p = wikipedia.page(fullName)
                hit += 1
            except PageError:
                skipped += 1
            except DisambiguationError:
                disambig += 1
