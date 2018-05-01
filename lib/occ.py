#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 12:57:10 2018

@author: alec
"""
import re

from nltk import sent_tokenize
from nltk.corpus import wordnet as wn
import csv
from csv import DictReader
from os import path
from collections import Counter
from itertools import chain

import g, nlp, wikidata

csv.field_size_limit(500 * 1024 * 1024)
allDocs = list( DictReader( open( path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" ) ) ) )

codeWordFn = path.join( path.dirname(__file__), "..", "coding", "allCodes.codeWord.csv" )
wordCodeFn = path.join( path.dirname(__file__), "..", "coding", "allCodes.wordCode.csv" )
allCodeFn = path.join( path.dirname(__file__), "..", "coding", "allCodes.csv" )
inFn = path.join( path.dirname(__file__), "..", "data","extracted.all.nice.csv" )

class Doc:
    def __init__(self, info):
        self.info = info

        self.id = info['fName']

        self.coded = False
        self.coding = None
        self.guess = None

        # avoid heavy computations!
        self._age = None
        self._fS = None
        self._spacy = None
        self._name = None
        self._nameS = None

    def dump(self):
        if not self.coded:
            raise Exception("Cannot dump what's not been coded!")

        import json
        d = {}
        d['age'] = self.age
        d['guess'] = self.guess
        d['nameS'] = self.nameS

        return json.dumps(d)

    def load(self, d):
        import json
        d = json.loads(d)

        self._age = d['age']
        self._nameS = d['nameS']
        self.guess = d['guess']

        self.coded = True

    def __str__(self):
        return str(self.spacy)

    @property
    def name(self):
        if self._name is None:
            self._name = next(self.fS.noun_chunks)
        return self._name

    @property
    def nameS(self):
        if self._nameS is None:
            self._nameS = str(self.name).strip()
        return self._nameS

    @property
    def spacy(self):
        if self._spacy is not None:
            return self._spacy

        spacy = nlp.nlp(self.info['fullBody'])
        self._spacy = spacy
        return spacy

    @property
    def fS(self):
        if self._fS is not None:
            return self._fS

        fS = extractFirstSentence(self.info['fullBody'])
        fS = nlp.nlp(fS.strip())
        self._fS = fS
        return fS

    @property
    def age(self):
        if self._age is not None:
            return self._age

        g.p.pdepth = 0

        lastName = self.nameS.split()[-1]

        rgxs = [
            r"(?:Mr\.?|Mrs\.?)\s*%s\s*was\s*([0-9]{1,3})(?:\s*years\s*old)?" % lastName,
            r"(?:She|He)\s*was\s*([0-9]{1,3})(?:\s*years\s*old)?",
            r"died.*at\s+the\s+age\s+of\s+([0-9]{1,3})",
            r"was\s*([0-9]{1,3})\s*years\s*old",
            r"was\s*([0-9]{1,3})",
            r"([0-9]{1,3})\s*years\s*old",
            r"was\s*believed\s*to\s*be([^,\.]*)",
            r"was\s*in\s*(?:his|her)\s*([^,\.]*)",
            r"([0-9]{1,3})",
        ]

        sents = list(self.spacy.sents)

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
            self._age = age
            return age


    def code(self, coding):
        assert isinstance(coding, Coder)

        self.coded = True
        self.coding = coding

        if len(self.fS) == 0:
            if self.coding.debug:
                g.p("Skipping. No content after trim.")
            coding.stateCounter.update(["zeroLengthSkip"])
            return

        if self.coding.debug:
            g.p.depth = 0
            g.p()
            g.p(self.fS)

            g.p.depth += 1

        lookhimup = set()

        if len(self.nameS) > 0:
            words = wikidata.lookupFamous(self.nameS)
            for x in words:
                lookhimup.update(coding.getOccCodes(x))

            if len(lookhimup) > 0:
                if self.coding.debug:
                    g.p("WikiData returns %s which gives OCC %s" % (words, lookhimup))

        if self.coding.debug:
            g.p("Extracted name: %s" % self.nameS)

        # extract information from the title
        dieWords = ['dies', 'die', 'dead']
        t = self.info['title']
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

            if self.coding.debug:
                g.p("Extracted from title:", tp)

        didSomething = False

        guesses = []

        # Alec McGail, scientist and genius, died today.
        nameChildren = list(self.name.root.children)
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

                if self.coding.debug and len(asWhat):
                    g.p('whoAs', asWhat)

                if len(asWhat):
                    didSomething = True

                # who was a scientist and inventor
                if v.pos_ == 'VERB':
                    if v.text in be:
                        for vc in v.children:
                            if vc.dep_ != 'attr':
                                continue

                            if self.coding.debug:
                                g.p('Expanded be verb', vc, vc.dep_)

                            # guesses.append(result)
                            didSomething = True

        finalGuess = []
        for guess in guesses:
            if len(guess['occ']) != 1:
                continue
            finalGuess.append(guess['occ'][0])

        if self.coding.debug:
            g.p("finalGuess", finalGuess)

        if True:
            moreGuesses = []
            # more stupid guesses...
            # literally expand every noun

            for w in self.fS:
                if w.pos_ != 'NOUN':
                    continue
                guess = coding.nounOCC(w)
                moreGuesses.append(guess)

            stupidFinalGuess = []
            for guess in moreGuesses:
                stupidFinalGuess += guess['occ']

            if self.coding.debug:
                g.p("stupidFinalGuess", stupidFinalGuess)

                if set(stupidFinalGuess) != set(finalGuess):
                    g.p("And they're different!", extrad=1)

        if not didSomething:
            if len(lookhimup) > 0:
                coding.stateCounter.update(["justWikidata"])
            else:
                if self.coding.debug:
                    g.p("Skipping. Strange grammatical construction.")
                coding.stateCounter.update(["strangeGrammar"])

class Coder:

    def __init__(self, debug=False, mode="firstSentence"):
        self.debug = debug

        # Initialize a bunch of variables
        self.w2c = {}
        self.allResults = []
        self.docs = []
        self.stateCounter = Counter()
        self.specificCounters = {}
        self.synMap = {}

        # Generate the W2C dictionary, used for all coding
        self.generateW2C()

    def loadCodes(self, fn):
        import os
        from os import path

        assert(os.path.isdir(fn))

        for d in self.docs:
            assert(isinstance(d, Doc))

            infn = path.join(fn, "%s.json" % d.id)

            with open( infn ) as inF:
                d.load(inF.read())

    def dumpCodes(self, fn):
        import os
        from os import path
        from shutil import rmtree

        if os.path.isdir(fn):
            if not g.query_yes_no("Directory exists. Replace?", default="no"):
                return
            rmtree(fn)

        os.mkdir(fn)

        for d in self.docs:
            assert(isinstance(d, Doc))

            outfn = path.join(fn, "%s.json" % d.id)

            with open( outfn, 'w' ) as outf:
                outf.write( d.dump() )

    def loadDocs(self, N=None, rand=True):
        import random
        with open(inFn) as inF:

            if N is None:
                self.docs = [Doc(info) for info in DictReader(inF)]
                return

            if rand:
                rs = DictReader(inF)
                rows = map(dict, rs)
                rows = list(rows)

                random.shuffle(rows)
                rows = rows[:N]
            else:
                rs = DictReader(inF)
                j = 0
                rows = []
                for r in rs:
                    rows.append(r)
                    j += 1
                    if j >= N:
                        break

        self.docs = [Doc(x) for x in rows]

    def docsByOcc(self, occ):
        occ = "occ2000-%s" % occ
        from itertools import chain
        return [doc for doc in self.docs if occ in list(chain.from_iterable(guess['occ'] for guess in doc.guess)) ]

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
        ns = wn.morphy(str(n))
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
        ndocs = len(self.docs)

        for index, d in enumerate(self.docs):
            # every now and then, let us know how it's going!
            if time() - lastPrintTime > 5:
                secondsLeft = int( ( float(ndocs) - index ) * (time() - startTime) / index )
                print("coding document %s/%s. ETA: %s" % (index, ndocs, timedelta(seconds=secondsLeft)))
                lastPrintTime = time()

            d.code(coding=self)

    def generateW2C(self):
        print("Extracting word2code dictionary")
        w2c = {}

        with open(allCodeFn) as allCodeF:
            dr = DictReader(allCodeF)
            codes = list(dr)

        for d in codes:
            theseC = d['code(s)'].split(",")
            theseC = [x.strip() for x in theseC]

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

            if d['term'] not in w2c:
                w2c[d['term']] = []
            w2c[d['term']] += theseC

        nw2c = {}

        # filter out non-OCC2000 codes

        for k, theseC in w2c.items():
            if len(k.split()) != 1:
                continue

            def fCode(c):
                try:
                    n = int(c.lower().split("occ2000-")[1])
                except ValueError:
                    return False

                if 620 <= n < 900:
                    return False
                return True

            nc = [c for c in theseC if 'occ2000' in c]
            nc = list(filter(fCode, nc))
            if len(nc) == 0:
                continue

            nw2c[k] = nc

        # my hand-coding

        nw2c['professor'] = ['occ2000-220']
        # w2c['scholar'] = ['occ2000-']
        nw2c['writer'] = ['occ2000-285']
        nw2c['photographer'] = ['occ2000-291']
        nw2c['filmmaker'] = ['occ2000-271']
        nw2c['football_player'] = ['occ2000-276']
        nw2c['composer'] = ['occ2000-285']  # is this true!?
        nw2c['virtuoso'] = ['occ2000-275']
        nw2c['politician.n.01'] = ['occ2000-003']
        nw2c['scholar'] = ['occ2000-186']  # not certain!
        nw2c['politician.n.02'] = ['political proponent']  # actually a specific definition. interesting

        # all except agent.n.02
        for x in wn.synset('representative.n.01').hypernyms():
            if x != nlp.wn.synset('agent.n.02'):
                nw2c[x.name()] = ['occ2000-003']

        nw2c['musician.n.01'] = nw2c['musician.n.02'] = ['occ2000-275']

        # add alternative words, whose codes are themselves
        altClass = ["volunteer", "thief", "defender", "champion", "veteran",
                                                                  "leader",
                    "philanthropist",
                    "benefactor",
                    "widow"]
        for aC in altClass:
            nw2c[aC] = [aC]

        nw2c['epidemiologist'] = ['occ2000-165']
        nw2c['painter'] = ['occ2000-260']
        nw2c['sculptor'] = ['occ2000-260']
        nw2c['player.n.01'] = ['occ2000-276']

        # now expand this vocabulary with synonyms:
        for k, v in nw2c.items():
            syn = nlp.synonyms(k)

            # synCodes = [ nw2c[x] for x in syn if x in nw2c ]
            # if len(set( tuple(sorted(x)) for x in synCodes )) > 2:
            #    continue

            for y in syn:
                self.synMap[y] = k

        self.w2c = nw2c

    def getSentences(self, word):
        for res in self.allResults:
            words = [x['word'] for x in res['guesses']]
            if word in words:
                yield res['sentence']


    def getBySubstr(self, substr):
        for res in self.allResults:
            if substr in res['sentence']:
                yield res['sentence']


    def whatWordsThisCode(self, c):
        initial = [x for x in list(self.w2c.keys()) if 'occ2000-%s' % c in self.w2c[x] and len(x.split()) == 1]
        synonyms = [ k for (k,v) in self.synMap.items() if v in initial]
        return initial+synonyms

    def getOccCodes(self, k):
        if k in self.synMap:
            k = self.synMap[k]

        if k in self.w2c:
            return self.w2c[k]

        return []

    def exportReport(self, fn):
        # make a simple count of OCC codes

        OCCsingle = Counter()
        OCCmultiple = Counter()
        OCCcomb = Counter()

        for d in self.docs:
            guesses = list(chain.from_iterable(y['occ'] for y in d.guess))
            if len(guesses) == 1:
                OCCsingle.update(guesses)

        # should it be fractional?
        for d in self.docs:
            guesses = list(chain.from_iterable(y['occ'] for y in d.guess))
            for y in guesses:
                OCCmultiple[y] += 1. / len(guesses)

        # or tuples?
        for d in self.docs:
            guesses = list(set(chain.from_iterable(y['occ'] for y in d.guess)))
            guesses = tuple(sorted(guesses))
            OCCcomb[guesses] += 1

        OCCgraph = Counter()
        # we could build a graph
        for d in self.docs:
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
                for doc in self.docs:
                    guesses = list(chain.from_iterable(guess['occ'] for guess in doc.guess))
                    if len(guesses) == 1 and guesses[0] == occ:
                        w("<p>%s</p>" % doc.fS)

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
    sentences = sent_tokenize(body)

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