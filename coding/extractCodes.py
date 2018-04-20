# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 13:50:48 2017

@author: alec
"""
import sys
from os import path
sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )
from lib import *

import numpy as np

from csv import reader, writer
import xlrd

wordCode = {}
codeWord = {}

occClassStr = {}
occClassFn = path.join( path.dirname(__file__), "..", "occupationalClassifications","directory of occupational titles (1).txt")
for line in open(occClassFn):
    split = line.split(",")
    
    for i, sp in enumerate(split):
        if sp.strip() == "":
            continue
        print(sp)
        print([ y in "0123456789-– " for y in sp.strip() ])
        if np.all([ y in "0123456789-– " for y in sp.strip() ]):
            print("breaking!")
            break
    
    s = ",".join( split[:i] ).strip().lower()
    c = ",".join( split[i:] ).strip()
    
    if s == '':
        continue
    if c == '':
        continue
    
    codes = getAllCodesFromStr(c)
    
    appendToKey( wordCode, s, c )
    appendToKey( codeWord, c, s )
    
    appendToKey( wordCode, s[:-1], c )
    appendToKey( codeWord, c, s[:-1] )

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

kat2 = {}

kat2Fn = path.join( path.dirname(__file__), "whatTheyWere_KZ.csv" )
with open(kat2Fn) as kat2F:
    katCsv = reader(kat2F)
    head = katCsv.next()
    
    for line in katCsv:
        codes = []
        for i in re.split("[/\*]", line[2]):
            try:
                codes.append(int(i))
            except ValueError:
                continue
        if len(codes) == 0:
            continue
        
        kat2[ line[0].lower() ] = codes

occ2000 = {}
occ2000Fn = path.join( path.dirname(__file__), "occ2000.xls" )
workbook = xlrd.open_workbook(occ2000Fn)
worksheet = workbook.sheet_by_index(0)

for row in range( 30960 ):
    code = worksheet.cell(row, 0).value
    code = "occ2000-%s"%code
    term = worksheet.cell(row, 2).value.lower()
    
    if "exc." in term:
        continue
    
    if code == "":
        continue
    
    justDelete = [
        "\ specified, not listed",
        "\ n.s.",
        ", n.e.c.",
        ", n.s.",
        "\ any other type"
    ]
    
    for de in justDelete:
        term = term.replace( de, "" )
    
    dontInclude = [
    ]
    
    tsplit = term.split(",")
    tsplit = [ x.strip() for x in tsplit ]
    tsplit = filter( lambda x: x not in dontInclude, tsplit )
    
    if len(tsplit) == 2:
        rearrange = " ".join( [ tsplit[1].strip(), tsplit[0].strip() ] )
        appendToKey( codeWord, code, rearrange )
        appendToKey( wordCode, rearrange, code )
    elif len(tsplit) > 2:
        print("skipped(2+ commas)", tsplit)
    else: # len(tsplit) == 1
        appendToKey( codeWord, code, term )
        appendToKey( wordCode, term, code )

    
allMappingsA = {}
allMappingsB = {}

ashFn = path.join( path.dirname(__file__), "firstSentences.moreInfo ash1.xls" )
workbook = xlrd.open_workbook(ashFn)
worksheet = workbook.sheet_by_index(0)

row = 1

while 1:
    first500 = worksheet.cell(row, 4).value.replace('\r', '\n')
    
    fn = worksheet.cell(row, 3).value

    def fixNums(num):
        if type(num) == int or type(num) == float:
            return [int(num)]
            
        num = num.replace("/", ",")
        num = num.replace("?", "")
        
        nums = []
        for i in re.split("[, ]", num):
            try:
                nums.append(int(i))
            except ValueError:
                continue
        return nums

    codeA = fixNums(worksheet.cell(row, 1).value)
    codeB = fixNums(worksheet.cell(row, 2).value)
    
    def fixNumsTup(tup):
        nums = []
        for i in re.split("[, /]", tup[0]):
            try:
                nums.append(int(i))
            except ValueError:
                continue
            
        return (nums, tup[1])
    
    tWNSq = re.findall("\[\s*([0-9/]+):([^\]]+)\]", first500)
    tWNSq = map( fixNumsTup, tWNSq )
    
    tWoNSq = re.findall("\[\s*([^0-9\]]+)\]", first500)
    tWoNSq = [(codeA, x) for x in tWoNSq]
    
    tWNCu = re.findall("\{\s*([0-9/]+):([^\}]+)\}", first500)
    tWNCu = map( fixNumsTup, tWNCu )
    
    tWoNCu = re.findall("\{\s*([^0-9\}]+)\}", first500)
    tWoNCu = [(codeB, x) for x in tWoNCu]
    
    
    for x in tWNSq + tWoNSq:
        key = x[1]
        key = " ".join( key.split() )
        key = key.lower()
        if key not in allMappingsA:
            allMappingsA[key] = []
            
        if key[0] == "[" and key[-1] == "]":
            allMappingsA[key[1:-1]] += x[0]
            allMappingsB[key[1:-1]] += x[0]
        else:
            allMappingsA[key] += x[0]
        
    for x in tWNCu + tWoNCu:
        key = x[1]
        key = " ".join( key.split() )
        key = key.lower()
        if key not in allMappingsB:
            allMappingsB[key] = []
        
        if key[0] == "{" and key[-1] == "}":
            allMappingsA[key[1:-1]] += x[0]
            allMappingsB[key[1:-1]] += x[0]
        else:
            allMappingsB[key] += x[0]
    
    row += 1
    
    if row > 105:
        break

ashFn = path.join( path.dirname(__file__), "firstSentences.moreInfo ds1.xlsx" )
workbook = xlrd.open_workbook(ashFn)
worksheet = workbook.sheet_by_index(0)

row = 980
    
while 1:
    first500 = worksheet.cell(row, 4).value.replace('\r', '\n')
    
    fn = worksheet.cell(row, 3).value

    def fixNums(num):
        if type(num) == int or type(num) == float:
            return [int(num)]
            
        num = num.replace("/", ",")
        num = num.replace("?", "")
        
        nums = []
        for i in re.split("[, ]", num):
            try:
                nums.append(int(i))
            except ValueError:
                continue
        return nums

    codeA = fixNums(worksheet.cell(row, 1).value)
    codeB = fixNums(worksheet.cell(row, 2).value)
    
    print(codeA, codeB)
    
    def fixNumsTup(tup):
        nums = []
        for i in re.split("[, /]", tup[0]):
            try:
                nums.append(int(i))
            except ValueError:
                continue
            
        return (nums, tup[1])
    
    tWNSq = re.findall("\[\s*([0-9/]+):([^\]]+)\]", first500)
    tWNSq = map( fixNumsTup, tWNSq )
    
    tWoNSq = re.findall("\[\s*([^0-9\]]+)\]", first500)
    tWoNSq = [(codeA, x) for x in tWoNSq]
    
    tWNCu = re.findall("\{\s*([0-9/]+):([^\}]+)\}", first500)
    tWNCu = map( fixNumsTup, tWNCu )
    
    tWoNCu = re.findall("\{\s*([^0-9\}]+)\}", first500)
    tWoNCu = [(codeB, x) for x in tWoNCu]
    
    
    for x in tWNSq + tWoNSq:
        key = x[1]
        key = " ".join( key.split() )
        key = key.lower()
        if key not in allMappingsA:
            allMappingsA[key] = []
        allMappingsA[key] += x[0]
        
    for x in tWNCu + tWoNCu:
        key = x[1]
        key = " ".join( key.split() )
        key = key.lower()
        if key not in allMappingsB:
            allMappingsB[key] = []
        allMappingsB[key] += x[0]
    
    row += 1
    
    if row > 1250:
        break

for key in allMappingsA:
    allMappingsA[key] = list(set(allMappingsA[key]))
for key in allMappingsB:
    allMappingsB[key] = list(set(allMappingsB[key]))
        
for s, c in occClassStr.items():
    if c.strip() == '':
        continue
    if len(str(c)) > 50:
        continue
    #outCodesCSV.writerow(["OccTitleAlec", s, c])
    if s not in wordCode:
        wordCode[s] = []
    wordCode[s] += ["OccCode-%s" % x.strip() for x in c.split(",")]
    
    for ci in c.split(","):
        ci = ci.strip()
        if "OccCode-%s" % ci not in codeWord:
            codeWord["OccCode-%s" % ci] = []
        codeWord["OccCode-%s" % ci].append(s)

for cat, words in musicalWords.items():
    for word in words:
        if word not in wordCode:
            wordCode[word] = []
        wordCode[word].append( "KZ-Music" )
        
        if "KZ-Music" not in codeWord:
            codeWord["KZ-Music"] = []
        codeWord["KZ-Music"].append(word)
        #outCodesCSV.writerow(["KZ-Music", word, cat])
            
for word, codes in allMappingsA.items():     
    if len(str(word)) > 50:
        continue           
    if len(str(codes)) > 50:
        continue
    if word not in wordCode:
        wordCode[word] = []
    wordCode[word] += [ "isco08-%s" % x for x in codes ]
    
    for code in codes:
        code = str(code).strip()
        if "isco08-%s" % code not in codeWord:
            codeWord["isco08-%s" % code] = []
        codeWord["isco08-%s" % code].append(word)
    #outCodesCSV.writerow(["Abdulla/David isco08", word, codes])

for word, codes in allMappingsB.items():      
    if len(str(word)) > 50:
        continue    
    if len(str(codes)) > 50:
        continue       
    
    if word not in wordCode:
        wordCode[word] = []
    wordCode[word] += [ "naics-%s" % x for x in codes ]
    
    for code in codes:
        code = str(code).strip()
        if "naics-%s" % code not in codeWord:
            codeWord["naics-%s" % code] = []
        codeWord["naics-%s" % code].append(word)
    #outCodesCSV.writerow(["Abdulla/David naics", word, codes])
        
for word, codes in kat2.items():            
    #outCodesCSV.writerow(["KZ-whatTheyWere", word, codes])
    if word not in wordCode:
        wordCode[word] = []
    wordCode[word] += [ "isco08-%s" % x for x in codes]
    
    for code in codes:
        code = str(code).strip()
        if "isco08-%s" % code not in codeWord:
            codeWord["isco08-%s" % code] = []
        codeWord["isco08-%s" % code].append(word)
    
outCodesFn = inFn = path.join( path.dirname(__file__), "allCodes.wordCode.csv" )
with open( outCodesFn, 'w' ) as outCodesF:
    outCodesCSV = writer( outCodesF )
    outCodesCSV.writerow( ["word", "code(s)"] )
    for k,v in sorted(wordCode.items(), key=lambda x: x[0]):
        outCodesCSV.writerow( [k, ", ".join(v)] )
        
outCodesFn = inFn = path.join( path.dirname(__file__), "allCodes.codeWord.csv" )
with open( outCodesFn, 'w' ) as outCodesF:
    outCodesCSV = writer( outCodesF )
    outCodesCSV.writerow( ["word", "code(s)"] )
    for k,v in sorted(codeWord.items(), key=lambda x: x[0]):
        outCodesCSV.writerow( [k, ", ".join(v)] )
        
outCodesFn = inFn = path.join( path.dirname(__file__), "allCodes.csv" )
with open( outCodesFn, 'w' ) as outCodesF:
    outCodesCSV = writer( outCodesF )
    outCodesCSV.writerow( ["term", "code(s)"] )
    for code,v in sorted(codeWord.items(), key=lambda x: x[0]):
        for word in v:
            outCodesCSV.writerow( [word, code] )
