#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 12:57:10 2018

@author: alec
"""
import re
from os import path
from collections import Counter
from itertools import chain

import numpy as np

from csv import reader, writer
import xlrd

import csv
from csv import DictReader, DictWriter

import g, nlp, wiki



csv.field_size_limit(500 * 1024 * 1024)
allDocs = list( DictReader( open( path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" ) ) ) )

codeWordFn = path.join( path.dirname(__file__), "..", "coding", "allCodes.codeWord.csv" )
wordCodeFn = path.join( path.dirname(__file__), "..", "coding", "allCodes.wordCode.csv" )
inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )

def _problematic_for_pickling(val):
    if isinstance(val, nlp.spacy.tokens.span.Span):
        return True
    if isinstance(val, nlp.spacy.tokens.doc.Doc):
        return True

class Doc:
    def __init__(self, init_info={}):
        self._prop_cache = init_info

        self.isCoded = False
        self.myCoder = None

    def dump(self):
        if not self.isCoded:
            raise Exception("Cannot dump what's not been coded!")

        import pickle

        d = {
            k:v
            for k,v in self._prop_cache.items()
            if not _problematic_for_pickling(v)
        }

        return pickle.dumps(d)

    def load(self, d):
        import pickle
        d = pickle.loads(d)

        self._prop_cache = d

        self.isCoded = True

    def __str__(self):
        return str(self['spacyFullBody'])

    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    #           This section defines all the functionality of this object as a picklable dictionary,
    #                                  with lazy-generated attributes
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------

    def __getitem__(self, item):
        method_name = "_prop_%s" % item

        if item in self._prop_cache:
            return self._prop_cache[item]

        if not hasattr(self, method_name):
            raise AttributeError("This obituary has no property %s, and doesn't know how to generate it." % item)

        val = getattr(self, method_name)()
        self._prop_cache[item] = val
        return val

    def __setitem__(self, key, value):
        self._prop_cache[key] = value

    def keys(self):
        return self._prop_cache.keys()

    def _clear_spacy_props(self):
        todel = []

        for k,v in self._prop_cache.items():
            if _problematic_for_pickling(v):
                todel.append(k)

        for k in todel:
            del self._prop_cache[k]

    def _get_all_props(self):
        import inspect
        all_methods = inspect.getmembers(self, predicate=inspect.ismethod)
        all_method_names = [ x[0] for x in all_methods ]
        prop_methods = filter(lambda x: x[:len("_prop")] == "_prop", all_method_names)

        return prop_methods

    def _prop_spacyName(self):
        # name is ALMOST ALWAYS the first noun_chunk.
        try:
            return next( self['spacyFirstSentence'].noun_chunks )
        except StopIteration:
            return self['title']

    def _prop_nameS(self):
        return str(self['spacyName']).strip()

    def _prop_spacyFullBody(self):
        return nlp.spacy_parse(self['fullBody'])

    def _prop_firstSentence(self):
        return extractFirstSentence(self['fullBody']).strip()

    def _prop_spacyFirstSentence(self):
        return nlp.spacy_parse(self["firstSentence"])

    def _prop_age(self):
        g.p.pdepth = 0

        lastName = self["nameS"].split()[-1]

        rgxs = [
            r"(?:Mr\.?|Mrs\.?)\s*%s\s*was\s*([0-9]{1,3})(?:\s*years\s*old)?" % re.escape(lastName),
            r"(?:She|He)\s*was\s*([0-9]{1,3})(?:\s*years\s*old)?",
            r"died.*at\s+the\s+age\s+of\s+([0-9]{1,3})",
            r"was\s*([0-9]{1,3})\s*years\s*old",
            r"was\s*([0-9]{1,3})",
            r"([0-9]{1,3})\s*years\s*old",
            r"was\s*believed\s*to\s*be([^,\.]*)",
            r"was\s*in\s*(?:his|her)\s*([^,\.]*)",
            r"([0-9]{1,3})",
        ]

        sents = list(self['spacyFullBody'].sents)

        foundReasonableAge = False
        # look for these sentences, in order
        for rgx in rgxs:
            for s in sents:
                fAge = re.findall(rgx, s.text)
                if len(fAge) == 0:
                    continue

                for sAge in fAge:
                    try:
                        age = int(sAge)
                        if age > 120 or age < 5:
                            continue

                        foundReasonableAge = True
                        break
                    except ValueError:
                        continue

                if foundReasonableAge:
                    break

            if foundReasonableAge:
                break

        if foundReasonableAge:
            return age

    # _----------------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------------
    #                                                     END SECTION
    # _----------------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------------



    # bag of words approach
    def code(self, coding):
        assert isinstance(coding, Coder)

        self.isCoded = True
        self.myCoder = coding

        fs = extractFirstSentence(self["fullBody"])
        words = fs.split()

        def ntuples(N):
            return [ " ".join(words[i:i+N]) for i in range(len(words)-N) ]

        allTuples = words + ntuples(2) + ntuples(3) + ntuples(4)

        self['guess'] = []

        for tup in allTuples:
            if tup in term2code:
                c = term2code[tup]["code"]
                self['guess'].append({
                    "where": "first_sentence",
                    "word": tup,
                    "occ": [c]
                })

        self['age']
        self['spacyFirstSentence']
        self['nameS']

        self._clear_spacy_props()

    def code_dependency(self, coding):
        assert isinstance(coding, Coder)

        self.isCoded = True
        self.myCoder = coding

        if len(self['spacyFirstSentence']) == 0:
            if self.myCoder.debug:
                g.p("Skipping. No content after trim.")
            coding.stateCounter.update(["zeroLengthSkip"])
            return

        if self.myCoder.debug:
            g.p.depth = 0
            g.p()
            g.p(self['spacyFirstSentence'])

            g.p.depth += 1

        lookhimup = set()

        if len(self["nameS"]) > 0:
            words = wiki.lookupFamous(self["nameS"])
            for x in words:
                lookhimup.update(coding.getOccCodes(x))

            if len(lookhimup) > 0:
                if self.myCoder.debug:
                    g.p("WikiData returns %s which gives OCC %s" % (words, lookhimup))

        if self.myCoder.debug:
            g.p("Extracted name: %s" % self["nameS"])

        # extract information from the title
        dieWords = ['dies', 'die', 'dead']
        t = self['title']
        t = t.split("\n")[-1]  # gets rid of those gnarly prefixes
        ts = [x.strip() for x in re.split(r'[;,]|--', t)]
        ts = ts[1:]  # the name is always the first one

        for tp in ts:
            tpW = [x.lower() for x in nlp.word_tokenize(tp)]
            hasDeathWord = False
            for dW in dieWords:
                if dW in tpW:
                    hasDeathWord = True
            if hasDeathWord:
                continue

            # if it's a number, continue
            try:
                int(tp)
                continue
            except:
                pass

            if self.myCoder.debug:
                g.p("Extracted from title:", tp)

        didSomething = False

        guesses = []

        # Alec McGail, scientist and genius, died today.
        nameChildren = list(self["spacyName"].root.children)
        apposHooks = list(filter(lambda x: x.dep_ == 'appos', nameChildren))

        if len(apposHooks) > 0:
            didSomething = True

            # painter, scientist, and architect
            baseNouns = nlp.followRecursive(apposHooks, 'conj')

            # one of the first **novelists**
            for i, x in enumerate(baseNouns):
                if nlp.isPrepPhrase(x) and str(x) == 'one':
                    baseNouns[i] = nlp.enterPrepPhrase(x)[0]

            # now that the important "what they were" nouns are identified,
            #   identify what OCC they are
            for n in baseNouns:
                result = coding.nounOCC(n)

                coding.stateCounter.update([result['state']])
                coding.count(space=result['state'], key=result['word'])

                guesses.append(result)

        self.guess = guesses

        # Alec McGail, who ..., died today.
        relcls = list(filter(lambda x: x.dep_ == 'relcl', nameChildren))

        if len(relcls) > 0:
            g.p.depth += 1

        for relcl in relcls:
            # need to follow advcl and conj
            goDeep = nlp.followRecursive(relcl, ['advcl', 'conj'])
            be = ['was', 'became']
            for v in goDeep:
                # as _
                followPreps = nlp.followRecursive(v, ['relcl', 'prep', 'pobj'])
                asWhat = [x for x in followPreps if next(x.ancestors).text == 'as' and x.pos_ == 'pobj']

                if self.myCoder.debug and len(asWhat):
                    g.p('whoAs', asWhat)

                if len(asWhat):
                    didSomething = True

                # who was a scientist and inventor
                if v.pos_ == 'VERB':
                    if v.text in be:
                        for vc in v.children:
                            if vc.dep_ != 'attr':
                                continue

                            if self.myCoder.debug:
                                g.p('Expanded be verb', vc, vc.dep_)

                            # guesses.append(result)
                            didSomething = True

        finalGuess = []
        for guess in guesses:
            if len(guess['occ']) != 1:
                continue
            finalGuess.append(guess['occ'][0])

        if self.myCoder.debug:
            g.p("finalGuess", finalGuess)

        if False:
            moreGuesses = []
            # more stupid guesses...
            # literally expand every noun

            for w in self['spacyFirstSentence']:
                if w.pos_ != 'NOUN':
                    continue
                guess = coding.nounOCC(w)
                moreGuesses.append(guess)

            stupidFinalGuess = []
            for guess in moreGuesses:
                stupidFinalGuess += guess['occ']

            if self.myCoder.debug:
                g.p("stupidFinalGuess", stupidFinalGuess)

                if set(stupidFinalGuess) != set(finalGuess):
                    g.p("And they're different!", extrad=1)

        if not didSomething:
            if len(lookhimup) > 0:
                coding.stateCounter.update(["justWikidata"])
            else:
                if self.myCoder.debug:
                    g.p("Skipping. Strange grammatical construction.")
                coding.stateCounter.update(["strangeGrammar"])


class Coder:

    def __init__(self, debug=False, mode="firstSentence"):
        self.debug = debug

        # Initialize a bunch of variables
        self.allResults = []
        self.obituaries = []
        self.stateCounter = Counter()
        self.specificCounters = {}

        # Generate the W2C dictionary, used for all coding
        self.generateW2C()

    def generateW2C(self):
        self.w2c = {}
        for code in codes:
            self.w2c[ code['term'] ] = code['code']

    def loadPreviouslyCoded(self, loadDir, N=None, rand=True):
        import os
        from os import path

        loadDir = path.join(path.dirname(__file__), '..', 'codeDumps', loadDir)

        assert(os.path.isdir(loadDir))

        toLoad = os.listdir(loadDir)

        def produceDocs():
            global numLoaded
            # loop through the entire CSV and see if any are in what I need to load.
            with open(inFn) as inF:
                for info in DictReader(inF):
                    thisFn = "%s.pickle" % info['fName']
                    if not thisFn in toLoad:
                        continue

                    d = Doc(info)
                    with open(path.join(loadDir, thisFn), 'rb') as thisF:
                        d.load(thisF.read())

                    yield d

        self.obituaries = g.select(produceDocs(), N=N, rand=rand)

        print("loaded %s documents" % len(self.obituaries))

    def dumpCodes(self, dumpDir):
        import os
        from os import path
        from shutil import rmtree

        dumpDir = path.join(path.dirname(__file__), '..', 'codeDumps', dumpDir)

        if os.path.isdir(dumpDir):
            if g.query_yes_no("Directory exists. Replace? If no, will keep previous codes if there are no updates.", default="no"):
                rmtree(dumpDir)

        os.mkdir(dumpDir)

        for d in self.obituaries:
            assert(isinstance(d, Doc))

            outfn = path.join(dumpDir, "%s.pickle" % d['fName'])

            with open( outfn, 'wb' ) as outf:
                outf.write( d.dump() )

    def loadDocs(self, N=None, rand=True):
        with open(inFn) as inF:
            rows = DictReader(inF)
            rows = g.select(rows, N=N, rand=rand)

        self.obituaries = [Doc(dict(x)) for x in rows]

    def findObitsByInfo(self, **kwargs):
        found = []
        for d in self.obituaries:
            thisOneSucks = False
            for k in kwargs:
                if not d.info[ k ] == kwargs[ k ]:
                    thisOneSucks = True
                    break
            if not thisOneSucks:
                found.append(d)
        return found

    def findObitByInfo(self, **kwargs):
        import random
        findAll = self.findObitsByInfo(**kwargs)

        if len(findAll) == 0:
            return None

        return random.choice( findAll )

    def docsByOcc(self, occ):
        occ = "occ2000-%s" % occ
        from itertools import chain
        return [doc for doc in self.obituaries if occ in list(chain.from_iterable(guess['occ'] for guess in doc.guess))]

    def nounOCC(self, n):
        debug = self.debug

        # knownWords = ['member', 'merchant','professor','actor','engineer','scholar','songwriter','trustee','fighter']
        vagueWords = ['founder', 'director', 'president', 'member']
        kinshipWords = ['mother', 'father', 'uncle', 'aunt', 'daughter', 'son', 'grandson', 'granddaughter', 'neice',
                        'nephew', 'sister', 'brother', 'wife', 'husband']

        entities = [(e.start, e.end, e.text) for e in n.doc.noun_chunks]

        ret = {
            "word": str(n),
            "state": "unclassified",
            "preps": [],
            'occ': []
        }

        # we should try and stem / simplify the word to a canonical version used by wn
        ns = nlp.wn.morphy(str(n))
        if ns is None:
            ns = str(n)
        ns = ns.lower()

        ev = nlp.expandVague(n)
        if ev and debug:
            g.p("expanded to %s (of) %s" % (ns, ev), extrad=1)

        ret['preps'] = ev

        if ns in vagueWords:
            if debug:
                g.p("identified vague word %s" % ns)

            ret['state'] = 'vague'
            return ret

        if ns in kinshipWords:
            if debug:
                g.p("identified kinship word %s" % ns)

            ret['state'] = 'kinship'
            return ret

        occLookup = self.getOccCodes(ns)
        ret['occ'] = occLookup

        if len(occLookup) > 0:
            if len(occLookup) > 1:
                if debug:
                    g.p("multiple OCC for %s: %s" % (ns, occLookup))

                ret['state'] = "vague_occWords"
            else:
                if debug:
                    g.p("single OCC for %s: %s" % (ns, occLookup))

                ret['state'] = 'specific_occWords'

            return ret

        if debug:
            g.p("no OCC for %s" % ns)

        return ret

    def count(self, space=None, key=None):
        if space is None and key is None:
            raise Exception("I won't count None!")

        if space not in self.specificCounters:
            self.specificCounters[space] = Counter()
        # specificCounters[result['state']].update(result['occ'])
        self.specificCounters[space].update([key])

    def codeAll(self):
        from time import time
        from datetime import timedelta

        lastPrintTime = time()
        startTime = time()
        ndocs = len(self.obituaries)

        for index, d in enumerate(self.obituaries):
            # every now and then, let us know how it's going!
            if time() - lastPrintTime > 5:
                secondsLeft = int( ( float(ndocs) - index ) * (time() - startTime) / index )
                print("coding document %s/%s. ETA: %s" % (index, ndocs, timedelta(seconds=secondsLeft)))
                lastPrintTime = time()

            d.code(coding=self)

    def getSentences(self, word):
        for res in self.allResults:
            words = [x['word'] for x in res['guesses']]
            if word in words:
                yield res['sentence']


    def getBySubstr(self, substr):
        for res in self.allResults:
            if substr in res['sentence']:
                yield res['sentence']


    def whatWordsThisCode(self, code):
        return [x['term'] for x in codes if code == x['code']]
        #initial = [x for x in list(self.w2c.keys()) if 'occ2000-%s' % c in self.w2c[x] and len(x.split()) == 1]
        #synonyms = [ k for (k,v) in self.synMap.items() if v in initial]
        #return initial+synonyms

    def getOccCodes(self, term):
        return [x['code'] for x in codes if term == x['term']]

    def exportReport(self, fn):
        # make a simple count of OCC codes

        OCCsingle = Counter()
        OCCmultiple = Counter()
        OCCcomb = Counter()

        for d in self.obituaries:
            guesses = list(chain.from_iterable(y['occ'] for y in d.guess))
            if len(guesses) == 1:
                OCCsingle.update(guesses)

        # should it be fractional?
        for d in self.obituaries:
            guesses = list(chain.from_iterable(y['occ'] for y in d.guess))
            for y in guesses:
                OCCmultiple[y] += 1. / len(guesses)

        # or tuples?
        for d in self.obituaries:
            guesses = list(set(chain.from_iterable(y['occ'] for y in d.guess)))
            guesses = tuple(sorted(guesses))
            OCCcomb[guesses] += 1

        OCCgraph = Counter()
        # we could build a graph
        for d in self.obituaries:
            guesses = list(set(chain.from_iterable(y['occ'] for y in d.guess)))
            for x1 in guesses:
                for x2 in guesses:
                    if x1 >= x2:
                        continue
                    OCCgraph[(x1, x2)] += 1

        with open("%s.html" % fn, 'w') as outf:
            def w(*args, **kwargs):
                outf.write(*args, **kwargs)

            w("<h1>20 Top Single Occupations</h1>")
            for occ, count in OCCsingle.most_common(20):
                w("<h2 id='%s'>%s had %s obituaries</h2>" % (occ, occ, count))
                for doc in self.obituaries:
                    guesses = list(chain.from_iterable(guess['occ'] for guess in doc.guess))
                    if len(guesses) == 1 and guesses[0] == occ:
                        w("<p>%s</p>" % doc['spacyFirstSentence'])

    def extractCodes(self, doc):

        mySuccessfulCodes = []

        wTokens = nlp.word_tokenize(doc)

        # one word...
        for i in range(len(wTokens)):
            word = wTokens[i]
            if word in self.w2c:
                # print word
                mySuccessfulCodes += self.w2c[word]

        # two words...
        for i in range(len(wTokens) - 1):
            word = " ".join([wTokens[i], wTokens[i + 1]])
            if word in self.w2c:
                # print word
                mySuccessfulCodes += self.w2c[word]

        # three words...
        for i in range(len(wTokens) - 2):
            word = " ".join([wTokens[i], wTokens[i + 1], wTokens[i + 2]])
            if word in self.w2c:
                # print word
                mySuccessfulCodes += self.w2c[word]

        return mySuccessfulCodes

    def extractCodesDetailed(self, doc):

        mySuccessfulCodes = []

        wTokens = nlp.word_tokenize(doc)

        # one word...
        for i in range(len(wTokens)):
            word = wTokens[i]
            if word in self.w2c:
                # print word
                mySuccessfulCodes += [
                    {
                        "code": c,
                        "word": word
                    } for c in self.w2c[word]
                ]

        # two words...
        for i in range(len(wTokens) - 1):
            word = " ".join([wTokens[i], wTokens[i + 1]])
            if word in self.w2c:
                # print word
                mySuccessfulCodes += [
                    {
                        "code": c,
                        "word": word
                    } for c in self.w2c[word]
                    ]

        # three words...
        for i in range(len(wTokens) - 2):
            word = " ".join([wTokens[i], wTokens[i + 1], wTokens[i + 2]])
            if word in self.w2c:
                # print word
                mySuccessfulCodes += [
                    {
                        "code": c,
                        "word": word
                    } for c in self.w2c[word]
                    ]

        return mySuccessfulCodes


    def extractCodesOnly2000(self, doc):
        mySuccessfulCodes = []

        wTokens = nlp.word_tokenize( doc )

        # one word...
        for i in range( len( wTokens ) ):
            word = wTokens[i]
            if word in self.w2c:
                for c in self.w2c[word]:
                    if "2000" in c:
                        mySuccessfulCodes.append(c)

        # two words...
        for i in range( len( wTokens ) - 1 ):
            word = " ".join( [wTokens[i], wTokens[i+1]] )
            if word in self.w2c:
                for c in self.w2c[word]:
                    if "2000" in c:
                        mySuccessfulCodes.append(c)


        # three words...
        for i in range( len( wTokens ) - 2 ):
            word = " ".join( [wTokens[i], wTokens[i+1], wTokens[i+2]] )
            if word in self.w2c:
                for c in self.w2c[word]:
                    if "2000" in c:
                        mySuccessfulCodes.append(c)


        return mySuccessfulCodes

def extractFirstSentence(body):
    sentences = nlp.sent_tokenize(body)

    if len(sentences) < 2:
        print("skipping(tooFewSentences)")
        return ""

    fS = sentences[0].strip()
    fS = " ".join( fS.split() )

    reStartStrip = [
        "[A-Z\s]+,.{1,30}[0-9]+\s*", # city and date
        "\(AP\) -\s*", # AP tag
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


def getRandomDocs(num):
    from random import sample
    return sample( allDocs, num )

def regenerateW2C(expandSynonyms = False):

    codegen = []

    if False:
        # these seem to be complete shit.
        # why did I run these!?
        occClassFn = path.join(path.dirname(__file__), "..", "w2c_source", "occupational titles.txt")
        print("Extracting terms from the OCC titles file %s" % occClassFn)

        # loop through each line in the OCC titles file
        for line in open(occClassFn):
            # comma-separate the line
            split = line.split(",")

            # loops through commas until an entry that represents an OCC code
            for i, sp in enumerate(split):
                if sp.strip() == "":
                    continue

                if np.all([y in "0123456789-– " for y in sp.strip()]):
                    break

            # now we construct the two parts
            phrase = ",".join(split[:i]).strip().lower()
            coded_occ = ",".join(split[i:]).strip()

            if phrase == '':
                continue
            if coded_occ == '':
                continue

            this_codes = g.getAllCodesFromStr(coded_occ)

            for code in this_codes:
                codegen.append({
                    "term":phrase,
                    "code":code,
                    "source":"occupational titles.txt"
                })

        if False:
            # ---------------   KATHERINE'S FILE   ----------------
            # I used to load these, but they're not exactly corresponding to OCC categories
            # so we'll just skip for now...

            musicalWords = {}
            musicalFn = path.join(path.dirname(__file__), "..", "occupationalClassifications", "Music Signifiers_KZ.csv")
            with open(musicalFn) as musicalCsvF:
                musicalCsv = reader(musicalCsvF)
                head = musicalCsv.next()

                for row in musicalCsv:
                    for i, cat in enumerate(head):
                        if cat.strip() not in ["", "Occupation", "Verbs"]:
                            if cat not in musicalWords:
                                musicalWords[cat] = []
                            if row[i].strip() == "":
                                continue

                            musicalWords[cat].append(row[i])

            kat2 = {}

            kat2Fn = path.join(path.dirname(__file__), "whatTheyWere_KZ.csv")
            with open(kat2Fn) as kat2F:
                katCsv = reader(kat2F)
                head = katCsv.next()

                for line in katCsv:
                    codegen = []
                    for i in re.split("[/\*]", line[2]):
                        try:
                            codegen.append(int(i))
                        except ValueError:
                            continue
                    if len(codegen) == 0:
                        continue

                    kat2[line[0].lower()] = codegen

    # ---------------   ABDULLAH'S FILE   ----------------
    # now we're going to parse through Abdullah's file
    occ2000Fn = path.join(path.dirname(__file__), "..", "w2c_source", "occ2000.xls")
    print("Extracting terms from Abdullah's OCC codes file %s" % occ2000Fn)
    workbook = xlrd.open_workbook(occ2000Fn)

    for wksheet_i in list(range(3, 17)):
        worksheet = workbook.sheet_by_index(wksheet_i)
        print("Working on worksheet %s" % wksheet_i)

        for row in range(10000):
            print(row)
            try:
                code = worksheet.cell(row, 0).value
            except IndexError:
                break

            term = worksheet.cell(row, 3).value
            if type(term) == int:
                continue

            term = term.lower()

            if "exc." in term:
                continue

            if code == "":
                print("Breaking in worksheet %s at row %s" % (wksheet_i, row))
                break

            terms = term.split("|")

            justDelete = [
                "\ specified, not listed",
                "\ n.s.",
                ", n.e.c.",
                ", n.s.",
                "\ any other type"
            ]

            for term in terms:

                thisOneBad = False
                for de in justDelete:
                    if de in term:
                        thisOneBad = True
                if thisOneBad:
                    continue

                if "," in term:
                    continue

                term = term.strip()
                if term == "":
                    continue

                codegen.append({
                    "term": term,
                    "code": code,
                    "source": "occ2000_updated.xls"
                })
                #print((code, term))

    # my hand-coding
    handCFN = path.join(path.dirname(__file__), "..", "w2c_source", "hand-coding.csv")
    with open(handCFN) as handCF:
        for c in DictReader(handCF):
            c['source'] = "hand-coding.csv"
            codegen.append(c)

    # all except agent.n.02
    for x in nlp.wn.synset('representative.n.01').hypernyms():
        if x != nlp.wn.synset('agent.n.02'):
            codegen.append({
                "term": x.name(),
                "code": "003",
                "source": "hand-coded-synset"
            })

    # add alternative words, whose codes are themselves
    altClass = ["volunteer", "thief", "defender", "champion", "veteran",
                "leader",
                "philanthropist",
                "benefactor",
                "widow"]

    for aC in altClass:
        codegen.append({
            "term": aC,
            "code": aC,
            "source": "alt"
        })

    # strip whitespace from terms
    for code in codegen:
        code['term'] = code['term'].strip()

    # SKIP EVERYTHING WITH MORE THAN ONE WORD :'((((
    # codegen = [ x for x in codegen if len(x['term'].split()) < 2 ]

    # IF THERE ARE MULTIPLE DETERMINATIONS FOR A SINGLE WORD, SKIP
    unique_term_code = set( (x['term'],x['code']) for x in codegen )
    count_terms = Counter( x[0] for x in unique_term_code )
    codegen = [ x for x in codegen if count_terms[ x['term'] ] == 1 ]

    if expandSynonyms:
        # now expand this vocabulary with synonyms:
        newcodes = []
        for c in codegen:
            # I guess somehow some of these are malformed!?
            if "term" not in c:
                print("wtf is this:", c)
                continue

            syn = nlp.synonyms(c['term'])

            for y in syn:
                newcodes.append({
                    "term": y,
                    "code": c['code'],
                    "source": "synonym:%s" % c['term']
                })
        codegen += newcodes

    # and export the CSV
    CSV_keys = list(sorted(set( chain.from_iterable([x.keys() for x in codegen]) )))
    CSV_fn = path.join(path.dirname(__file__), "..", "w2c_source", "compiledCodes.csv")
    with open(CSV_fn, 'w') as outCodesF:
        CSV_w = DictWriter(outCodesF, fieldnames=CSV_keys)
        CSV_w.writeheader()
        for code in codegen:
            CSV_w.writerow(code)

    print( "CSV successfully written at '%s'" % CSV_fn)

codes = None
term2code = {}
CSV_fn = path.join(path.dirname(__file__), "..", "w2c_source", "compiledCodes.csv")
print("Loading term-code associations into variable 'codes' from %s..." % CSV_fn)
print("Loading term dictionary into variable 'term2code' from %s..." % CSV_fn)
with open(CSV_fn, 'r') as outCodesF:
    CSV_r = DictReader(outCodesF)
    codes = list(CSV_r)

for code in codes:
    term2code[ code["term"] ] = code

# startStruct = [
#     ['DET', 'NOUN', 'PUNCT', 'NOUN', 'PUNCT', 'CCONJ', 'NOUN'],
#     ['DET', 'ADJ', 'NOUN', 'CCONJ', 'NOUN'],
#     ['DET', 'ADJ', 'ADJ', 'NOUN', 'CCONJ', 'NOUN'],
#     ['DET', 'NOUN', 'NOUN', 'CCONJ', 'NOUN'],
#     ['DET', 'NOUN', 'CCONJ', 'NOUN'],
#     ['DET', 'VERB', 'ADJ', 'NOUN'],
#     ['DET', 'VERB', 'NOUN', 'NOUN'],
#     ['DET', 'ADJ', 'NOUN'],
#     ['DET', 'NOUN'],
#     ['NOUN', 'PUNCT', 'NOUN', 'PUNCT', 'CCONJ', 'NOUN'],
#     ['NOUN', 'CCONJ', 'NOUN']
# ]
#
# if struct == "None":
#     for ss in startStruct:
#         if posFind(ss, whw) == 0:
#             struct = "|".join(ss)
#             break

def _codeToName():
    c2n = {}
    officialTitlesFn = path.join(path.dirname(__file__), '..', 'coding', 'occ2000.officialTitles.csv')
    with open(officialTitlesFn) as officialTitlesF:
        for row in DictReader(officialTitlesF):
            if row['officialTitle'] == "":
                continue

            code = "%03d" % int(row['code'])

            c2n[code] = row['officialTitle']

    return c2n

codeToName = _codeToName()
