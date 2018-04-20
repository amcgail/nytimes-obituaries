# -*- coding: utf-8 -*-

import csv

from os import path
from csv import DictReader
import json
from nltk import sent_tokenize, word_tokenize
import spacy
import re

debug = False

codeWordFn = path.join( path.dirname(__file__), "..", "coding", "allCodes.codeWord.csv" )
wordCodeFn = path.join( path.dirname(__file__), "..", "coding", "allCodes.wordCode.csv" )
allCodeFn = path.join( path.dirname(__file__), "..", "coding", "allCodes.csv" )

def loadNLP():
    global nlp
    if 'nlp' not in globals():
        print("nlp not found in global namespace. Loading...")
        print("NOTE: this variable is huge, and can eat up memory. Don't load in multiple terminals.")
        nlp = spacy.load('en')

def allCodes():
    with open(allCodeFn) as allCodeF:
        dr = DictReader(allCodeF)
        codes = list(dr)
    return codes

def firstSentence(body):
    sentences = sent_tokenize(body)
    
    if len(sentences) < 2:
        print("skipping(tooFewSentences)")
        return ""
    
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
        
    return firstSentence

def code2word():
    pass

def getAllCodesFromStr( codestr ):
    try:
        codes = json.loads( codestr )
        if type(codes) != list:
            codes = [codes]
    except:
        codes = codestr.split(",")
        codes = [x.strip() for x in codes]
    
    codes = [ str(x) for x in codes ]
    codes = [ x.replace("\xe2\x80\x93", "-") for x in codes ]
    
    # deal with dashes...
    newcs = []
    for c in codes:
        
        if "-" in c:
            try:
                s, e = c.split("-")
                ilen = len(s)
                
                s = int(s)
                e = int(e)
                newc = [ ("%0" + str(ilen) + "d") % i for i in range(s, e+1) ]
                newcs += newc
            except:
                print("skipping(malformed)", c)
                continue
            
            #print c, newc
        else:
            newcs.append(c)
            
    codes = newcs
    return codes
    

def appendToKey( d, key, newItem ):
    if key not in d:
        d[key] = []
    if type(newItem) == list:
        d[key] += newItem
    else:
        d[key].append(newItem)    
    
def word2code():
    print("Extracting word2code dictionary")
    ret = {}
    for d in allCodes():
        codes = d['code(s)'].split(",")
        codes = [ x.strip() for x in codes ]
        
        """
        if d['origin'] == 'OccTitleAlec':
            if "-" in codestr:
                #print codestr
                #print newcs
                pass
        
        if d['origin'] == 'OccTitleAlec':
            codes = ["occ-%s" % x for x in codes]
        if d['origin'] == 'KZ-Music':
            codes = ["music"]
        if d['origin'] == 'Abdulla/David isco08':
            codes = ["isco08-%s" % x for x in codes]
        if d['origin'] == 'Abdulla/David naics':
            codes = ["naics-%s" % x for x in codes]
        if d['origin'] == 'KZ-whatTheyWere':
            codes = ["isco08-%s" % x for x in codes]
        """
        
        if d['term'] not in ret:
            ret[ d['term'] ] = []
        ret[ d['term'] ] += codes
    
    return ret
    
w2c = word2code()

def extractCodesDetailed(doc):
    
    global countOcc2000
    
    mySuccessfulCodes = []
        
    wTokens = word_tokenize( doc )
    
    # one word...
    for i in range( len( wTokens ) ):
        word = wTokens[i]
        if word in w2c:
            #print word
            mySuccessfulCodes += [
                { 
                    "code": c,
                    "word": word
                } for c in w2c[word]
            ]
            
    # two words...
    for i in range( len( wTokens ) - 1 ):
        word = " ".join( [wTokens[i], wTokens[i+1]] )
        if word in w2c:
            #print word
            mySuccessfulCodes += [
                { 
                    "code": c,
                    "word": word
                } for c in w2c[word]
            ]


    # three words...
    for i in range( len( wTokens ) - 2 ):
        word = " ".join( [wTokens[i], wTokens[i+1], wTokens[i+2]] )
        if word in w2c:
            #print word
            mySuccessfulCodes += [
                { 
                    "code": c,
                    "word": word
                } for c in w2c[word]
            ]
            
    return mySuccessfulCodes

# I don't remember why this is here...
countOcc2000 = {}

def extractCodes(doc):
    global countOcc2000
    
    mySuccessfulCodes = []
        
    wTokens = word_tokenize( doc )
    
    # one word...
    for i in range( len( wTokens ) ):
        word = wTokens[i]
        if word in w2c:
            #print word
            mySuccessfulCodes += w2c[word]
            
            
            for c in w2c[word]:
                if "2000" in c:
                    if word not in countOcc2000:
                        countOcc2000[word] = 0
                    countOcc2000[word] += 1
                    break
            
    # two words...
    for i in range( len( wTokens ) - 1 ):
        word = " ".join( [wTokens[i], wTokens[i+1]] )
        if word in w2c:
            #print word
            mySuccessfulCodes += w2c[word]
            
            for c in w2c[word]:
                if "2000" in c:
                    if word not in countOcc2000:
                        countOcc2000[word] = 0
                    countOcc2000[word] += 1
                    break

    # three words...
    for i in range( len( wTokens ) - 2 ):
        word = " ".join( [wTokens[i], wTokens[i+1], wTokens[i+2]] )
        if word in w2c:
            #print word
            mySuccessfulCodes += w2c[word]
            
            for c in w2c[word]:
                if "2000" in c:
                    if word not in countOcc2000:
                        countOcc2000[word] = 0
                    countOcc2000[word] += 1
                    break
            
    return mySuccessfulCodes
    
def extractCodesOnly2000(doc):
    global countOcc2000
    
    mySuccessfulCodes = []
        
    wTokens = word_tokenize( doc )
    
    # one word...
    for i in range( len( wTokens ) ):
        word = wTokens[i]
        if word in w2c:
            for c in w2c[word]:
                if "2000" in c:
                    mySuccessfulCodes.append(c)
            
    # two words...
    for i in range( len( wTokens ) - 1 ):
        word = " ".join( [wTokens[i], wTokens[i+1]] )
        if word in w2c:
            for c in w2c[word]:
                if "2000" in c:
                    mySuccessfulCodes.append(c)
            

    # three words...
    for i in range( len( wTokens ) - 2 ):
        word = " ".join( [wTokens[i], wTokens[i+1], wTokens[i+2]] )
        if word in w2c:
            for c in w2c[word]:
                if "2000" in c:
                    mySuccessfulCodes.append(c)
            
            
    return mySuccessfulCodes

def followRecursive(tree):
    total = []
    for x in tree['modifiers']:
        total += followRecursive(x)
    
    del tree['modifiers']

    total.append(tree)
    return total

def extractNV(doc):
    loadNLP()
    doc = nlp(unicode(doc))
    tree = doc.print_tree()[0]
    N = []
    V = []
    for x in followRecursive(tree):
        #arc = x['arc']
        #print x
        if x['POS_coarse'] == "NOUN":
            N.append( x['lemma'] )
        if x['POS_coarse'] == "VERB":
            V.append( x['lemma'] )
    return {
        "N": N,
        "V": V
    }
    
def extractLexical(doc, name):
    
    nameParts = re.split("[\s\.]", name)
    nameParts = [x.lower() for x in nameParts]
    nameParts = [x for x in nameParts if len(x) > 3]
    
    whatHeDid = set()
    whatHeWas = set()
    sentences = sent_tokenize(doc)
    
    loadNLP()
    
    for s in sentences:
        s = unicode(s)
        
        #print "-------------"
        if debug:
            print(" ".join( s.split() ))
        doc = nlp(s)
        
        verbGroup = {}
        
        for chunk in doc.noun_chunks:
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
            else:
                for info in verbGroup[vi]:
                    for np in nameParts:
                        if np in info[0].lower():
                            wD = info[-1]
                            wD = " ".join( wD.split() )
                            whatHeDid.add( wD )
    return {
        "did": list(whatHeDid),
        "was": list(whatHeWas)
    }
    
def extractFirstSentence(body):
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
    
    return firstSentence
    
csv.field_size_limit(500 * 1024 * 1024)
allDocs = list( DictReader( open( path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" ) ) ) )
    
def getRandomDocs(num):
    from random import sample
    return sample( allDocs, num )
