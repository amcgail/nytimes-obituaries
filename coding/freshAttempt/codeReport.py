#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 10:59:16 2018

@author: alec
"""

from csv import writer

import sys
from os import path
basedir = path.join( path.dirname(__file__), '..', ".." )
sys.path.append( path.join( basedir, 'lib' ) )
import occ, nlp

mycoder = occ.Coder()

with open('codeReport.html', 'w') as outf:
    def w(*args, **kwargs):
        outf.write(*args, **kwargs)
        
    occs = set()
    for word in mycoder.w2c:
        occs.update( mycoder.w2c[word] )
    
    w("<h1>Keywords by occupation</h1>")
    for occ in sorted(list(occs)):
        w("<p>")
        w("<b>%s</b>:   " % occ)
        for x in mycoder.w2c:
            if occ in mycoder.w2c[x]:
                w("(%s) " % x)
                for z in mycoder.synMap:
                    if mycoder.synMap[z] == x:
                        w("%s, " % z)
        w("</p>")
        
with open('codes.csv', 'w') as outf:
    csvw = writer(outf)
    csvw.writerow(["OCC", "word", "primary"])

    occs = set()
    for x in mycoder.w2c:
        occs.update( mycoder.w2c[x] )
    for occ in sorted(list(occs)):
        for x in mycoder.w2c:
            if occ in mycoder.w2c[x]:
                csvw.writerow([occ, x, 1])
                for z in nlp.synonyms(x):
                    csvw.writerow([occ, z, 0])