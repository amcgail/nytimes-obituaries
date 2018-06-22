# -*- coding: utf-8 -*-
import json
import sys

debug = False

def select(iterator, N=None, start=0, rand=True):
    import itertools
    import random

    if N is None:
        return list(iterator)

    if rand:
        rs = list(iterator)
        random.shuffle(rs)
        return rs[start:start+N]
    else:
        return list( itertools.islice(iterator, start, start+N) )

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
    

def appendToKey(d, key_list, item_list):
    if type(key_list) != list:
        key_list = [key_list]

    for key in key_list:
        if key not in d:
            d[key] = []
        if type(item_list) == list:
            d[key] += item_list
        else:
            d[key].append(item_list)

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

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
