# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 22:10:50 2017

@author: abdullahts
"""

###Rename the mainfiels

import os
import re
import numpy as np

from os import path


#source2 = "/home/alec/data projects/NYTIMESobituaries" # File path where all files are located
source2 = "../" # File path where all files are located

os.chdir(source2)

import codecs

allNonUTFChars = set()

sourceDir = "allobitmainfiles"
destDir = "allobitfilesStripped"

if not os.path.exists(destDir):
    os.mkdir(destDir)

for f in os.listdir(sourceDir):
    filename, file_ext = os.path.splitext(f)
    yearpart = filename.split("The_New_York_Times")[1]
    y = path.join( destDir, "A-NYT" + yearpart +  ".txt" )
    print(y) 
    with codecs.open(f, 'r', "ISO-8859-1") as infile, open(y, "w") as outfile:
        for line in infile:
            isUTF = [ ord(c) >= 128 for c in line ]
            
            allNonUTFChars = allNonUTFChars.union([ c for c in line if ord(c) >= 128 ])
            
            line = "".join( [ c for c in line if ord(c) < 128 ] )
            
            if np.any(isUTF):
                #print (isUTF)
                #print (line)
                pass
                
                #print( [ line[i] for i in range(isUTF) if not isUTF[i] ]  )
            
            if not line.strip():
                continue
            else: 
                outfile.write(line)
            


#for f in os.listdir():
#    name = 'A-NYT'
    #year1 = 1
    #counter = 0
    #file = 1
#    with open(f) as nfile:
        #fullThing = nfile.read()
#        yearpart = f.split("The_New_York_Times")[1]
        #year = yearpart[0:4]
        #if counter > 0:
#        newfilename = name  + "-" + yearpart#us the first 50 characters of nameLine in file ID
  
#        print(newfilename)
        
#        fout = open(newfilename + ".txt", "w")
        
        
#    with open(f) as inputfile:
#        fullText = inputfile.read()
#        fout.write(fullText)
#    inputfile.close()
#    fout.close()
        