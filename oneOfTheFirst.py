#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 13:58:40 2018

@author: alec
"""

import csv
from nltk import sent_tokenize
from os import path
        
csv.field_size_limit(500 * 1024 * 1024)
inFn = path.join( path.dirname(__file__), "data","extracted.all.nice.csv" )

print("Extracting docs...")
with open(inFn) as inF:
    docs = list( csv.DictReader(inF) )

dcount = 0
scount = 0

i = 0

for d in docs:
    i += 1
    if i % 1000 == 0:
        print( "doc %s" % i )
    
    if "one of the first" not in d['fullBody']:
        continue
    dcount += 1
    for s in sent_tokenize(d['fullBody']):
        if "one of the first" in s:
            scount += 1
            what = s.split("one of the first")[1]
            what = " ".join( what.split() )
            what = "+ " + what
            #print(what)