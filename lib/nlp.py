#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 12:46:36 2018

@author: alec
"""
import collections
import re
from operator import itemgetter

import spacy

from nltk.corpus import wordnet as wn
from pptree import print_tree
from nltk import word_tokenize, sent_tokenize
from nameparser import HumanName as HumanNameOld

import g
from g import debug

import gender_guesser.detector as gender
gender_detector = gender.Detector()

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

class _inquirer_lexicon:
    def __init__(self):
        self.lexicon = None

    def load(self):
        from os import path
        if self.lexicon is not None:
            return

        print("Loading general inquirer lexicon from disk...")
        inquirer_lexicon_path = path.join(path.dirname(__file__), "..", "generalInquirerLexicon", "inqdict.txt")

        self.lexicon = {}
        with open(inquirer_lexicon_path) as inq_f:
            lines = inq_f.read().split("\n")
            lines = lines[1:]

            for l in lines:
                lsp = l.split()
                if len(lsp) < 2:
                    continue

                (word, source) = lsp[0:2]
                dictionaries = " ".join( lsp[2:] )
                dictionaries = dictionaries.split("|")[0]
                dictionaries = dictionaries.split()

                word = word.split("#")[0]

                for d in dictionaries:

                    if d not in self.lexicon:
                        self.lexicon[d] = set()

                    self.lexicon[d].add(word)

    def __getitem__(self, item):
        self.load()
        return self.lexicon[item]

    def dictionaries(self):
        self.load()
        return sorted(list(self.lexicon.keys()))

    def countWords(self, lexiconName, doc):
        self.load()

        count = 0
        for x in word_tokenize(doc):
            if x.upper() in self.lexicon[lexiconName]:
                count += 1

        return count

inquirer_lexicon = _inquirer_lexicon()

def first_name(name):
    name = name.lower()
    not_first_names = ["mr","dr",""]
    names = re.split(r'[\.\s]', name)
    inc = 0
    first = names[inc]
    while first in not_first_names:
        inc += 1
        if inc >= len(names):
            first = None
            break

        first = names[inc]

    return first

def last_name(name):
    name = name.lower()
    names = re.split(r'[\.\s]', name)
    not_last_names = ["3d", "jr", "iii", ""]

    inc = 1
    last = names[-inc]
    while last in not_last_names:
        inc += 1
        if inc >= len(names):
            last = None
            break

        last = names[-inc]

    return last

def names_match_list(nl1, nl2):
    names1 = [(first_name(n), last_name(n)) for n in nl1]
    names2 = [(first_name(n), last_name(n)) for n in nl2]

    matches = []

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
        total += followRecursiveNLTK(x)
    
    del tree['modifiers']

    total.append(tree)
    return total

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

class _lemmatizerC:
    def __init__(self):
        self.lemmatizer = None

    def load(self):
        if self.lemmatizer is not None:
            return

        print("Loading lemmatizer...")
        from nltk.stem import WordNetLemmatizer
        self.lemmatizer = WordNetLemmatizer()


    def __call__(self, *args, **kwargs):
        self.load()
        return self.lemmatizer.lemmatize(*args, **kwargs)

lemmatize = _lemmatizerC()

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

# Efficiency notes:
#
# getTuples:
#   20 word sentence, 1-4 tuples
#   = 20 + 19 + 18 + 17 = 74
#
# getCloseUnorderedTuples:
#    20 word sentence, 1-4 tuples
#    = 20 + 19*2

def getTuples(words, minTuple, maxTuple):
    def ntuples(N):
        return [tuple(words[i:i + N]) for i in range(len(words) - N + 1)]

    allTuples = []
    for i in range(minTuple, maxTuple+1):
        allTuples += ntuples(i)

    return list(set(allTuples))

def getCloseUnorderedSets(words, minTuple, maxTuple, maxBuffer=1):
    from itertools import combinations, chain

    def ntuples(N):
        return set(frozenset(words[i:i + N]) for i in range(len(words) - N + 1))

    allSets = set()
    for i in range(minTuple, maxTuple+1):

        for buffer in range(maxBuffer+1):


            originalTuples = ntuples(i + buffer)
            toAdd = set( frozenset(y) for y in chain.from_iterable( combinations(x, i) for x in originalTuples ) )

            allSets.update(toAdd)

    return allSets

def tupleBaggerAndSearch(doc, dictionary):
    allTuples = getTuples(word_tokenize(doc), 1, 4)
    allTuples = [" ".join(x) for x in allTuples]
    return bagOfWordsSearch(allTuples, dictionary)

def bagOfWordsSearch(bag, dictionary):
    extracted = []

    for word in bag:
        if word in dictionary:
            extracted.append( dictionary[word] )

    return extracted

def isTitleCase(str):
    words = str.split()
    for w in words:
        w = w.strip()
        fl = w[0]
        if fl.lower() == fl:
            return False

    return True

class HumanName(HumanNameOld):
    def __init__(self, *args, **kwargs):
        self._gender = None
        super(HumanName, self).__init__(*args, **kwargs)

    @property
    def gender(self):
        # generate the property if we don't have it already
        if self._gender is None:
            gendr = 'unknown'
            if self.first:
                gendr = gender_detector.get_gender(self.first)
            if self.title:
                if self.title.lower() in ['princess', 'ms.', 'mrs.', 'queen']:
                    gendr = 'female'
                if self.title.lower() in ['mr.', 'prince', 'king']:
                    gendr = 'male'

            self._gender = gendr

        return self._gender

    def supercedes(self, compare):
        import string

        # if the last name is there, it must match
        if compare.last != self.last:
            return False

        # if the first name is there, it must match
        if compare.first and self.first:
            # handling initials
            if self.is_an_initial(compare.first) or self.is_an_initial(self.first):
                if self.first[0].lower() != compare.first[0].lower():
                    return False
            else:
                if self.first != compare.first:
                    return False

        # if the middle name is there, it must match
        if compare.middle and self.middle:
            # handling initials
            if self.is_an_initial(compare.middle) or self.is_an_initial(self.middle):
                if self.middle[0].lower() != compare.middle[0].lower():
                    return False
            else:
                if self.middle != compare.middle:
                    return False

        # make sure the genders match --
        # note -- only if there's no first name
        if not compare.first and compare.title:
            # Mr. Mrs.
            m = ["Mr."]
            f = ["Mrs.", "Ms."]

            if compare.title in m and self.gender == 'female':
                print("Skipping", compare)
                return False
            elif compare.title in f and self.gender == 'male':
                print("Skipping", compare)
                return False

        # also, Jr.'s are important!
        # only if there's a first name and last name
        if compare.first and compare.last:
            if compare.suffix or self.suffix:
                if compare.suffix != self.suffix:
                    return False

        return True


def isFullName(string):
    blacklist = ["university", "universities", "college", "city", "center", "medical", "county", "school", 'hospital']
    l = string.lower()
    for b in blacklist:
        if b in l:
            return False

    if len(string.split()) < 2:
        return False
    if not isTitleCase(string):
        return False

    n = HumanName(string)
    if not n.first:
        return False

    if gender_detector.get_gender(n.first) == 'unknown':
        # if there's a first name, it should be gendered
        return False

    return True


def isPossibleFullName(string):
    blacklist = ["university", "universities", "college", "city", "center", "medical", "county", "school", 'hospital']
    l = string.lower().split()

    if len(l) < 2:
        return False
    for b in blacklist:
        if b in l:
            return False

    if not isTitleCase(string):
        return False

    n = HumanName(string)
    if not n.first:
        return False

    if len(n.last) < 2:
        return False

    # must be ASCII
    if not all( (65 <= ord(x) <= 122) for x in n.first+n.last ):
        return False

    return True




def replace_many_ranges_at_once( str, ranges, withWhat ):
    # need to sort the ranges for this to work
    # this should sort by the first element of each range, which is what we want

    if type(withWhat) != list:
        return replace_many_ranges_at_once(str, ranges, [withWhat]*len(ranges))

    sorting_enumeration = sorted( enumerate(ranges), key=itemgetter(1) )
    indices = list(map(itemgetter(0), sorting_enumeration))
    ranges = list(map(itemgetter(1), sorting_enumeration))

    withWhat = list(map(lambda i: withWhat[i], indices))

    parts = []
    current_i = 0
    for range_i, range in enumerate(ranges):
        # cut to the start of the range
        parts.append(str[ current_i : range[0] ])
        # add the what
        parts.append(withWhat[range_i])
        # update current_i
        current_i = range[1]+1

    parts.append(str[current_i:])

    return "".join(parts)

def tokenize_list_as(full_body, to_replace, withWhat):
    for rep in to_replace:
        full_body = re.sub(
            "([^a-zA-Z])%s([^a-zA-Z])" % re.escape(rep), # need to find non-word chars around it
            r'\1%s\2'%withWhat, # need to preserve the whitespace
            full_body
        )

    return full_body

def tokenize_ents_spacy(full_body, ent_types):
    # must be from this collection!
    assert not len(set(ent_types) - {"GPE","PERSON","DATE","NORP","PRODUCT","ORG"})

    fb_spacy = spacy_parse(full_body)

    replacement_info = [ (x.start_char, x.end_char-1, x.label_) for x in fb_spacy.ents if x.label_ in ent_types ]
    ranges = list(map( itemgetter(0, 1), replacement_info ))
    withWhat = list(map(itemgetter(2), replacement_info))
    withWhat = list(map(lambda x: "<sp:%s>"%x, withWhat))

    return replace_many_ranges_at_once(full_body, ranges=ranges, withWhat=withWhat)

def tokenize_name(full_body, name):
    debug_level = 0

    mpp = ["he", "his", "him", "himself"]
    fpp = ["she", "her", "hers", "herself"]

    fb_spacy = spacy_parse(full_body)
    name_to_replace = HumanName(name)

    to_replace = []

    if debug_level:
        print("------------------------")
        print(name, name_to_replace.gender)
        print(full_body)

    # look for any time they actually say the guy's name, but maybe in another way
    # Mr. Marcelloni was great man...
    for noun_chunk in fb_spacy.noun_chunks:
        maybename_str = str(noun_chunk)
        compare = HumanName(maybename_str)

        if not name_to_replace.supercedes( compare ):
            continue

        to_replace.append(noun_chunk)

    # now we're interested in
    personal_pronouns = filter(lambda x: x.tag_ in ['PRP','PRP$'], fb_spacy)
    mypp = mpp * (name_to_replace.gender == 'male') + fpp * (name_to_replace.gender == 'female') + (mpp+fpp) * (name_to_replace.gender not in ['female','male'])
    personal_pronouns = filter(lambda x: str(x).lower() in mypp, personal_pronouns)

    name_mentions = list(filter(lambda x: isFullName(str(x)), fb_spacy.noun_chunks))

    # because pp are always gendered, I can filter those names whose gender doesn't match
    def exclude_by_gender( ogender, name_str ):
        #print("exclusion script", ogender, name_str)
        name = HumanName(name_str)
        if name.first:
            fnameGender = gender_detector.get_gender(name.first)
            if ogender == 'male' and fnameGender =='female':
                return False
            if ogender == 'female' and fnameGender =='male':
                return False

        if name.title:
            if ogender == 'male' and name.title.lower() in ['ms.','mrs.']:
                return False
            if ogender == 'female' and name.title.lower() in ['mr.']:
                return False

        return True

    print(name_mentions)
    name_mentions = list(filter(lambda x: exclude_by_gender(ogender=name_to_replace.gender, name_str=str(x)), name_mentions))
    print(name_mentions)

    if debug_level > 1:
        print("NAMES:", name_mentions)

    for pp in personal_pronouns:

        # idk any other way to do this. create a span and then get start_char
        ppspan = pp.doc[pp.i:pp.i+1]
        ppstart = ppspan.start_char

        name_mentions_before_me = filter(lambda x: x.start_char < ppstart, name_mentions)
        try:
            last_name_mention = max(name_mentions_before_me, key=lambda x: x.start_char)
        except ValueError:
            # there were none before me...
            continue

        # make sure his name was the last one spoken
        if not name_to_replace.supercedes( HumanName(str(last_name_mention)) ):
            continue

        if debug_level > 1:
            print(pp, last_name_mention)
            print(ppspan.sent, last_name_mention.sent)

        to_replace.append(ppspan)

    if debug_level > 0:
        print(to_replace)

    ranges = [ (x.start_char, x.end_char-1) for x in to_replace ]
    tokenized = replace_many_ranges_at_once(full_body, ranges, "<obiturized>")

    return tokenized


def extractFirstSentence(body):
    sentences = nlp.sent_tokenize(body)

    if len(sentences) < 2:
        # print("skipping(tooFewSentences)")
        return ""

    fS = sentences[0].strip()
    fS = " ".join( fS.split() )

    # FAIRFAX, Va. <start>
    # HOPKINSVILLE, Ky. <start>
    # PORTLAND, Ore. <start>

    reStartStrip = [
        "[A-Z\s\.]+,.{1,30}[0-9]+\s*", # city and date
        ".*\(AP\)\s*-*\s*", # AP tag
        #".*-{2,}\s*", # Blah Blah Blah -- Start of thing is here
        "[A-Z]{3,},?\s+[A-Za-z]+\s*(\(.*\))?\s*(--)?\s*", # e.g. MONTEVIDEO, Uruguay (with optional parens :() --
        "([A-Z]{2,}[:\.,]?\s*)+[^a-zA-Z]*", #just all caps, probably bad --, but ignore the first real letter :)
    ]

    for patt in reStartStrip:
        findTag = re.match(patt, fS)
        if findTag:
            fS = fS[findTag.end():]

    if "," not in fS:
        fS += " " + " ".join( sentences[1].strip().split() )

    fS = fS.replace("Late Edition - Final\n", "")
    fS = fS.replace("Correction Appended\n", "")
    fS = fS.replace("The New York Times on the Web\n", "")
    fS = fS.replace("National Edition\n", "")

    # for those "LONDON --"s
    fS = re.sub(r'^[A-Z\s\(\)]*(--)\s+', '', fS)

    # OMG
    # this simply gets rid of a date at the beginning of the line.
    monthDateRe = r"^(\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?(\d{1,2}\D?)?\D?((19[7-9]\d|20\d{2})|\d{2})\.?\s*"
    fS = re.sub(monthDateRe, '', fS)

    return fS