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
import spacy

from nltk import sent_tokenize

import re

if 'nlp' not in locals():
     nlp = spacy.load('en')

from os import path

inFn = path.join( path.dirname(__file__), "..", "data/extracted.nice.csv" )
#outFn = "/home/alec/data projects/NYTIMESobituaries/extracted.noBody.nice.abberations.csv"

whatAnyoneDid = {}
whatAnyoneWas = {}

debug = False

def followNoun(w, tree):
    pass

def followRecursive(tree):
    total = []
    for x in tree['modifiers']:
        total += followRecursive(x)
    
    del tree['modifiers']

    total.append(tree)
    return total

with open(inFn) as inF:
    rs = reader(inF)
    
    head = rs.next()
    
    n = 0
    for r in rs:
        if n > 1000:
            break
        n += 1
        if n%100 == 0:
            break
            print n
        
        body = r[head.index('fullBody')]
        name = r[head.index('name')]
        nameParts = re.split("[\s\.]", name)
        nameParts = [x.lower() for x in nameParts]
        nameParts = [x for x in nameParts if len(x) > 3]
        
        namePartSkips = ["dead"]
        nameParts = [x for x in nameParts if x not in namePartSkips]
        
        sentences = sent_tokenize(body)
        
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
        clause = nlp(unicode(commaSplit[1]))
        
        whatHeIs = []
        whatHeDid = []
        
        #print commaSplit[1]
        tree = clause.print_tree()[0]
        import json
        #print json.dumps( tree, indent=4 )

        for x in followRecursive(tree):
            #arc = x['arc']
            #print x
            if x['POS_coarse'] == "NOUN":
                whatHeIs.append( x['lemma'] )
            if x['POS_coarse'] == "VERB":
                whatHeDid.append( x['lemma'] )

        print whatHeDid, whatHeIs

# import random

# if False:
#     with open('whatAnyoneWas.csv', 'w') as csvF:
#         w = writer(csvF)
#         w.writerow(["what","count","examples"])
#         for word in whatAnyoneWas:
#             samp = whatAnyoneWas[word]['examples']
#             samp = random.sample(samp, min(len(samp), 5))
#             samp = "||".join(samp)
            
#             w.writerow([word,whatAnyoneWas[word]['count'],samp])
            
#     with open('whatAnyoneDid.csv', 'w') as csvF:
#         w = writer(csvF)
#         w.writerow(["what","count","examples"])
#         for word in whatAnyoneDid:
#             samp = whatAnyoneDid[word]['examples']
#             samp = random.sample(samp, min(len(samp), 5))
#             samp = "||".join(samp)
            
#             w.writerow([word,whatAnyoneDid[word]['count'],samp])