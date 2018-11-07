# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 23:16:42 2017

"""

#step1: extract individual obituary

# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 12:51:01 2017


"""

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## STEP-- Split into smaller files and save
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

import os
import re

source2 = "/home/alec/data projects/NYTIMESobituaries" # File path where all files are located

os.chdir(source1)
print(os.getcwd())

inDir = "allmainfiles_stripped"

#outDir = inDir+"_individual"
outDir = inDir + "_ind"

if not os.path.exists(outDir):
    os.mkdir(outDir)

for f in os.listdir(inDir):
    filename, file_ext = os.path.splitext(f)
    print(filename)
    y = filename
    with open(os.path.join( inDir, f )) as nfile:
         op = ''
         start = 0
         counter = 1
         for x in nfile.read().split("\n"):
             if re.match("\s*Copyright [0-9]{4} The New York Times Company\s*", x) is None:
                 if x.strip() == '':
                     continue
                 
                 if op == '':
                     op = x
                 else:
                     op = op + '\n' + x
                     #op = op + x
                     
             else: 
                 start = 1
                 #print(op)

             
                 with open(os.path.join(outDir,"Indobit" + "-" + y + "-" + str(counter) + '.txt'), 'w') as outputfile:
                     outputfile.write(op)
                     outputfile.close()
                     op = ''
                     counter+=1