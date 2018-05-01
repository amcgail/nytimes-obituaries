# -*- coding: utf-8 -*-
import csv
import json
from csv import DictReader
from os import path

debug = False

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

class _p:
    def __init__(self):
        self.outf = None
        self.depth = 0
        pass

    def openOutF(self, fn):
        self.outf = open(fn, 'w')

    def closeOutF(self):
        if self.outf is None:
            print("No outf to close")
            return

        self.outf.close()
        self.outf = None

    def __call__(self, *s, extrad=0):
        s = " ".join( str(ss) for ss in s )
        if self.outf is None:
            print('.' * (self.depth + extrad) + str(s))
        else:
            print( '.'*(self.depth+extrad) + str(s), file=self.outf )

p = _p()