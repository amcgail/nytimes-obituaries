#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 12:46:36 2018

@author: alec
"""
import re

import spacy
from nltk.corpus import wordnet as wn
from pptree import print_tree
from nltk import word_tokenize, sent_tokenize

import g
from g import debug

# this SpaCy object is so large, we should wait to load it until it's needed
class _nlp:
    def __init__(self):
        self.nlp = None
        self.restricted = False

    def load(self):
        if self.restricted:
            raise Exception("I refuse to load SpaCy. In restricted mode.")
        if self.nlp is None:
            print("nlp not found in global namespace. Loading...")
            print("NOTE: this variable is huge, and can eat up memory. Don't load in multiple terminals.")
            self.nlp = spacy.load('en')

    def __call__(self, *args, **kwargs):
        self.load()
        return self.nlp(*args, **kwargs)

spacy_parse = _nlp()

def first_name(name):
    name = name.lower()
    not_first_names = ["mr","dr",""]
    names = re.split(r'[\.\s]', name)

    inc = 0
    last = names[inc]
    while last in not_first_names:
        inc += 1
        last = names[inc]

    return last

def last_name(name):
    name = name.lower()
    names = re.split(r'[\.\s]', name)
    not_last_names = ["3d", "jr", "iii", ""]

    inc = 1
    last = names[-inc]
    while last in not_last_names:
        inc += 1
        last = names[-inc]

    return last

def names_match_list(nl1, nl2):
    names1 = [(first_name(n), last_name(n)) for n in nl1]
    names2 = [(first_name(n), last_name(n)) for n in nl2]

    for i, (fn1, ln1) in enumerate(names1):
        for j, (fn2, ln2) in enumerate(names2):
            # last names should match exactly
            if ln1 != ln2:
                continue

            # what about initials?
            if len(fn1) == 1:
                if fn1 != fn2[0]:
                    continue
            elif len(fn2) == 1:
                if fn2 != fn1[0]:
                    continue

            # under normal circumstances,
            #  require the first names to be equal...
            if fn1 != fn2:
                continue

            #if we've gotten this far, we have a match!
            matches.append((i,j))

    return matches

def names_match(n1, n2):
    fn1 = first_name(n1)
    fn2 = first_name(n2)
    ln1 = last_name(n1)
    ln2 = last_name(n2)

    # last names should match exactly
    if ln1 != ln2:
        return False

    # what about initials?
    if len(fn1) == 1:
        if fn1 != fn2[0]:
            return False
    elif len(fn2) == 1:
        if fn2 != fn1[0]:
            return False

    # under normal circumstances,
    #  require the first names to be equal...
    if fn1 != fn2:
        return False

    return True

def follow(ws, deps):
    from itertools import chain
    if type(ws) != list:
        ws = [ws]
    if type(deps) != list:
        deps = [deps]

    # cool feature :)
    childfollow = list(filter(lambda x: x[0]!="-", deps))

    ancestorfollow = list(filter(lambda x: x[0] == "-", deps))
    ancestorfollow = [ x[1:] for x in ancestorfollow ]

    return list(chain.from_iterable( [x for x in w.children if x.dep_ in childfollow] for w in ws)) + \
        list(chain.from_iterable([x for x in w.ancestors if w.dep_ in ancestorfollow] for w in ws))

def followRecursive(ws, deps, depth=0):
    if depth > 100:
        raise Exception("Infinite loop in followRecursive")

    if len(ws) == 0:
        return []

    if type(deps) != list:
        deps = [deps]
    if type(ws) != list:
        ws = [ws]

    def expandSpans(w):
        if hasattr(w, "root"):
            return w.root
        return w

    ws = list(map(expandSpans, ws))

    nextStep = follow(ws, deps)

    # prevent infinite recursion. do they have the same elements
    # print( set(nextStep) == set(ws), set(nextStep), set(ws) )
    # if set(nextStep) == set(ws):
    #     return nextStep

    return followRecursive(nextStep, deps, depth + 1) + ws

def followRecursiveNLTK(tree):
    total = []
    for x in tree['modifiers']:
        total += followRecursive(x)
    
    del tree['modifiers']

    total.append(tree)
    return total


def extractNV(doc):
    doc = spacy_parse.nlp(doc)
    tree = doc.print_tree()[0]
    N = []
    V = []
    for x in followRecursiveNLTK(tree):
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
    
# accepts a synset
def printHyponymTree(s):
    print_tree( synsetNode(s), "hyponyms" )
# accepts a synset
def printHyponymTrees(s):
    for ser in s.hypernyms():
        print_tree( synsetNode(ser), "hyponyms" )
        
def distanceToPerson(s):
    ds = s.hypernym_distances()
    for parent, d in ds:
        if parent == wn.synset('person.n.01'):
            return d
    
    # if it's not even a parent
    return -1

def synonyms(w):
    if '.' in w:
        parts = w.split('.')
        if len( parts ) < 3:
            return []
        
        try:
            int(parts[-1])
        except:
            return []
        
        s = wn.synset(w)
    else:
        ss = wn.synsets(w, pos='n')
    
        if len(ss) == 0:
            return []
        
        # THIS PART IS HARD AND ERROR-PRONE
        if True:
            # take the most specific definition
            s = max( ss, key=distanceToPerson )
    
    if distanceToPerson(s) > 1:
        hypo = lambda s: s.hyponyms()
        hypos = list(s.closure(hypo))
        
        allS = [s]+hypos
    else:
        allS = [s]
    
    #print(allS)
    
    syns = [x.name() for y in allS for x in y.lemmas()]
    syns = [x for x in syns if '_' not in x]# and x.lower() == x]
    
    return list(set(syns))

class synsetNode:

    def __init__(self, s):
        self.hyponyms = [ synsetNode(x) for x in s.hyponyms() ]
        
        self.s = s
        self.word = str(s)

    #def __str__(self):
    #    return self.function
    
    def __str__(self):
        return str(self.s)
    
def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def posSplit(seq, doc):
    i = 0
    splitAt = []
    for j, x in enumerate(doc):
        if x.pos_ == seq[i]:
            i += 1
        else:
            i = 0

        if i >= len(seq):
            splitAt.append(j + 1 - len(seq))
            i = 0

    if len(splitAt) == 0:
        return doc

    splits = []
    lastJ = -1
    for j in splitAt:
        g.p(lastJ)
        if lastJ < 0:
            splits.append(doc[:j])
        else:
            splits.append(doc[lastJ:j])
        lastJ = j + len(seq)
    splits.append(doc[lastJ:])
    return splits

def isPrepPhrase(w):
    for x in w.children:
        if x.dep_ == 'prep':
            return True
    return False


def enterPrepPhrase(w):
    s1 = follow(w, 'prep')

    ret = []
    for x in s1:
        ret += follow(x, 'pobj')

    return ret


def expandCompound(w):
    full = str(w)
    for x in w.children:
        if x.dep_ == 'compound':
            return expandCompound(x) + " " + full

    return full

def getContainingEntity(w):
    entities = [ (e.start, e.end, e.text) for e in w.doc.noun_chunks ]
    for e in entities:
        if w.i in range(e[0],e[1]):
            return e[2]
    return None

def expandVague(n):
    # ambiguous of what?
    ws = []
    for c in n.children:
        if c.dep_ == 'prep':
            for ofWhat in c.children:
                ws.append(ofWhat)

    ws = followRecursive(ws, 'conj')
    ws = map(getContainingEntity, ws)
    ws = filter(lambda x: x is not None, ws)
    return list(ws)

def posFind(seq, doc):
    i = 0
    for j, x in enumerate(doc):
        if x.pos_ == seq[i]:
            i += 1
        else:
            i = 0

        if i >= len(seq):
            return j+1-len(seq)
    return -1


def extractLexical(doc, name):

    nameParts = re.split("[\s\.]", name)
    nameParts = [x.lower() for x in nameParts]
    nameParts = [x for x in nameParts if len(x) > 3]

    whatHeDid = set()
    whatHeWas = set()
    sentences = sent_tokenize(doc)

    for s in sentences:
        s = str(s)

        #print "-------------"
        if debug:
            print(" ".join( s.split() ))
        doc = spacy_parse(s)

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

#==============================================================================
# months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
# months += [ m[:3] for m in months ]
# months += [ m[:3] + "." for m in months ]
# dayStr = "|".join( [ '"%s"' % i for i in range(31) ] )
# monthStr = "|".join( [ '"%s"' % i for i in months ] )
# places = ["home", "Manhattan"]
# placeStr = "|".join( [ '"%s"' % i for i in places ] )
#
# grammar1 = nltk.CFG.fromstring("""
#   Loc -> {placeStr}
#   Loc -> Loc "in" Loc
#   Month -> {monthStr}
#   Day -> {dayStr}
#   Date -> Month Day
#   Death -> "on" Date "at" Loc
#   Death -> "on" Date "in" Loc
# """.format(**locals()))
#==============================================================================

# pattern1 = [{'POS':'VERB', 'OP':'!'}, {'POS': 'CCONJ'}, {'POS': 'DET', 'OP':'?'}, {'POS': 'ADV', 'OP': "*"}, {'POS': 'ADJ', 'OP': "*"}, {'POS': 'NOUN', 'OP': "+"}]
# pattern2 = [{'POS':'VERB', 'OP':'!'}, {'POS': 'DET'}, {'POS': 'ADV', 'OP': "*"}, {'POS': 'ADJ', 'OP': "*"}, {'POS': 'NOUN', 'OP': "+"}]
# matcher = Matcher(nlp.nlp.vocab)
# matcher.add('adjNoun', None, pattern1) # add pattern
# matcher.add('adjNoun', None, pattern2) # add pattern

# ==============================================================================
# Similarity measures
# ==============================================================================

# ==============================================================================
#             maxi = -1
#             maxs = -1
#             for x in knownWords + vagueWords + occWords:
#                 w1 = wn.synsets(str(n))
#                 w2 = wn.synsets(x)
#                 if len(w1) == 0 or len(w2) == 0:
#                     continue
#
#                 simComp = [ w1i.path_similarity( w2i ) for w1i in w1 for w2i in w2 ]
#                 simComp = list(filter( lambda x: x is not None, simComp ))
#                 if len(simComp) == 0:
#                     continue
#
#                 sim = max(simComp)
#
#                 if sim > maxs:
#                     maxi = x
#                     maxs = sim
#
#             if maxi != -1:
#                 print("mostSimilar", str(n), maxi, maxs)
# ==============================================================================

# TRYING TO CREATE HYPONYM SETS TO CLASSIFY A LARGE SET OF WORDS

# hyponymSets = {}
#
# for w1 in mycoder.specificCounters['unclassified']:
#     ss = wn.synsets(w1)
#     if len(ss) == 0:
#         # print(w1, "has no definition")
#         continue
#
#     s = ss[0]
#     hyp = s.hyponyms()
#
#     myhyp = []
#
#     for w2 in mycoder.specificCounters['unclassified']:
#         if w1 == w2:
#             continue
#
#         ss2 = wn.synsets(w2)
#         if any(x in hyp for x in ss2):
#             myhyp.append(w2)
#
#     hyponymSets[w1] = myhyp