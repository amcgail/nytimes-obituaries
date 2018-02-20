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
from nltk import sent_tokenize, word_tokenize
from os import path
from collections import Counter
import numpy as np
import re
import sys

sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )

from lib import *

if 'nlp' not in locals():
    import spacy
    nlp = spacy.load('en')

inFn = path.join( path.dirname(__file__), "..", "data","extracted.nice.csv" )

w2c = word2code()

debug = False

notCoded = []
coded = []

with open(inFn) as inF:
    rs = reader(inF)
    
    head = rs.next()
    
    n = 0
    for r in rs:
        # if n > 1000:
        #     break
        n += 1
        if n%10 == 0:
            #break
            print(n)
            
        if n > 100:
            break
            
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
        for lastThing, c in enumerate(commaSplit):
            if "died" in c.lower():
                break
            
        clause = ",".join( commaSplit[1:lastThing] )
        
        firstSentence = clause
        
        mySuccessfulCodes = []
        
        for word, codes in w2c.items():
            if word in word_tokenize( firstSentence ):
                mySuccessfulCodes += codes
        
        """
        for cat, words in musicalWords.items():
            for word in words:
                if re.search(r"\b%s\b"%re.escape(word.lower()), firstSentence.lower()) is not None:
                    mySuccessfulCodes.append("KZ-%s (%s)"%(cat,word))
                    
        for word, codes in allMappingsA.items():
            if re.search(r"\b%s\b"%re.escape(word.lower()), firstSentence.lower()) is not None:
                mySuccessfulCodes.append("isco08-%s (%s)"%("/".join(map(str,codes)), word))
        
        for word, codes in allMappingsB.items():
            if re.search(r"\b%s\b"%re.escape(word.lower()), firstSentence.lower()) is not None:
                mySuccessfulCodes.append("naics-%s (%s)"%("/".join(map(str,codes)), word))
                
        for word, codes in kat2.items():
            if re.search(r"\b%s\b"%re.escape(word.lower()), firstSentence.lower()) is not None:
                mySuccessfulCodes.append("naicsKZ-%s (%s)"%("/".join(map(str,codes)), word))
        """
        
        if len(mySuccessfulCodes) > 0:
            #print firstSentence, mySuccessfulCodes
            coded.append([r[head.index('fName')], firstSentence] + mySuccessfulCodes)
        else:
            notCoded.append([r[head.index('fName')], firstSentence] + mySuccessfulCodes)

if False:
    outCSVfn = path.join( path.dirname(__file__), "secondStabCoding.csv" )
                    
    with open(outCSVfn, 'w') as outF:
        outCSV = writer(outF)
        outCSV.writerow(["fn","clause", "codes"])
        
        for cr in coded:
            outCSV.writerow(cr)
            
    outCSVfn = path.join( path.dirname(__file__), "secondStabCoding.notCoded.csv" )
                    
    with open(outCSVfn, 'w') as outF:
        outCSV = writer(outF)
        outCSV.writerow(["fn","clause"])
        
        for cr in notCoded:
            outCSV.writerow(cr)