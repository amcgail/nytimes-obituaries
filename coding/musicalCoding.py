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
from nltk import sent_tokenize

import re

if 'nlp' not in locals():
     nlp = spacy.load('en')

from os import path
from collections import Counter

if "occClassStr" not in locals() or True:
    occClassStr = {}
    occClassFn = path.join( path.dirname(__file__), "..", "occupationalClassifications","directory of occupational titles (1).txt")
    for line in open(occClassFn):
        split = line.split(",")
        
        for i, sp in enumerate(split):
            try:
                int(sp)
                break
            except:
                pass
        
        s = ",".join( split[:i] ).strip().lower()
        c = ",".join( split[i:] )
        
        if s == '':
            continue
        
        occClassStr[s] = c
        occClassStr[s[:-1]] = c

if "musicalWords" not in locals() or True:
    musicalWords = {}
    musicalFn = path.join( path.dirname(__file__), "..", "occupationalClassifications", "Music Signifiers_KZ.csv" )
    with open(musicalFn) as musicalCsvF:
        musicalCsv = reader(musicalCsvF)
        head = musicalCsv.next()
        
        for row in musicalCsv:
            for i, cat in enumerate(head):
                if cat.strip() not in ["","Occupation","Verbs"]:
                    if cat not in musicalWords:
                        musicalWords[cat] = []
                    if row[i].strip() == "":
                        continue
                    
                    musicalWords[cat].append( row[i] )

inFn = path.join( path.dirname(__file__), "..", "data","extracted.nice.csv" )

debug = False

if True:
    coded = []
    
    with open(inFn) as inF:
        rs = reader(inF)
        
        head = rs.next()
        
        n = 0
        for r in rs:
            # if n > 1000:
            #     break
            n += 1
            if n%100 == 0:
                #break
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
            
            for s, c in occClassStr.items():
                if s in firstSentence:
                    coded.append([r[head.index('fName')], firstSentence, s, c])
                    print s
            
            for cat, words in musicalWords.items():
                for w in words:
                    if " %s " % w.lower() in firstSentence.lower():
                        coded.append([r[head.index('fName')], firstSentence, w, "KZ-%s"%cat])
    
outCSVfn = path.join( path.dirname(__file__), "naiveCoding.csv" )
                
with open(outCSVfn, 'w') as outF:
    outCSV = writer(outF)
    outCSV.writerow(["fn","firstSentence", "basedOn", "code"])
    
    for cr in coded:
        outCSV.writerow(cr)