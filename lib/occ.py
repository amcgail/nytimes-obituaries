#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 12:57:10 2018

@author: alec
"""

import csv
import re
from collections import Counter
from csv import DictReader, DictWriter
from csv import reader
from itertools import chain
from os import path, remove

import xlrd

import g
import nlp
import wiki

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


def nocache(f):
    f.to_cache = False
    return f


class Doc:
    def __init__(self, init_info={}):
        # the info it's initialized with has "_" before it, so everything on top is coded.
        init_info = {
            "_%s"%k : v
            for k,v in init_info.items()
        }
        self._prop_cache = init_info

        self.isCoded = False
        self.myCoder = None

    def destroy(self):
        remove(self['_relfn'])

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

        self._prop_cache.update(d)

        self.isCoded = True

    def __str__(self):
        return self['firstSentence']

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

    def __delitem__(self, key):
        del self._prop_cache[key]

    def __contains__(self, item):
        return item in self._prop_cache

    def keys(self):
        return self._prop_cache.keys()

    def _clear_spacy_props(self):
        todel = []

        for k,v in self._prop_cache.items():
            if _problematic_for_pickling(v):
                todel.append(k)

        for k in todel:
            del self._prop_cache[k]

    def _get_all_prop_methods(self):
        import inspect
        all_methods = inspect.getmembers(self, predicate=inspect.ismethod)
        all_method_names = [ x[0] for x in all_methods ]
        prop_methods = filter(lambda x: x[:len("_prop")] == "_prop", all_method_names)

        return list(prop_methods)

    def _get_all_props(self):
        return [x[len("_prop_"):] for x in self._get_all_prop_methods()]

    # the following two are no longer used
    def _prop_title(self):
        t = self['_title']
        t = t.split("\n")[-1].strip()  # gets rid of those gnarly prefixes
        return t

    def __prop_date(self):
        import datetime
        return datetime.datetime.strptime(self['_date'], "%B %d, %Y")

    def _prop_spacyName(self):
        name = None

        #print(self['firstSentence'])
        # most consistently, it's the first noun chunk:
        def isName(x):
            if len(x.split()) < 2:
                return False
            if not nlp.isTitleCase(x):
                return False
            return True

        # start with NER from spacy:
        if name is None:
            guesses = self['spacyFirstSentence'].ents
            guesses = [x for x in guesses if x.label_ == 'PERSON' and isName(x.text)]
            if len(guesses) > 0:
                # just use the first one
                # and we'll probably need expansion
                name = guesses[0].text
                #print("NER for the win")

        # first, expand. it many times doesn't get parens, or Dr. Rev. etc.
        # we then need to look deeper, if it's a "Mr." "Mrs." or "Dr."

        # then just try some noun chunking...
        if name is None:
            nc = list(self['spacyFirstSentence'].noun_chunks)
            if len(nc) > 0:
                nc = list(filter(isName, map(str, nc)))
                if len(nc) > 0:
                    name = nc[0]
                    #print("Noun Chunk Found!")

        if name is None:
            name = "<name not found>"
        return name
        #print(name)

        if False:
            # try spacy's NER:
            guesses = self['spacyFirstSentence'].ents
            guesses = [x for x in guesses if x.label_ == 'PERSON']
            print("FS:", self['firstSentence'])
            if len(guesses) > 0:
                print("Found:", [x.text for x in guesses])

        if True:
            import re
            # name is ALMOST ALWAYS the first noun_chunk.
            fsname = None
            nc = list( self['spacyFirstSentence'].noun_chunks )
            if len(nc) > 0:
                nc = list(filter(nlp.isTitleCase, map(str, nc)))
                if len(nc) > 0:
                    # print(nc)
                    pass
                # print("FS:", self['firstSentence'])
            return

            # also could just check that the words are in the title...
            if fsname is not None:
                t = self['title'].lower()
                tw = set(nlp.word_tokenize(t))
                fsnamew = set(nlp.word_tokenize(str(fsname).lower()))
                if len(tw.intersection(fsnamew)) > 0:
                    #print(fsname)
                    pass


            # the title is a good check
            if False:
                tname = self['title']
                pats = [
                    "is dead",
                    ",",
                    "dies",
                    "is slain",
                    "of",
                    "dead",

                ]
                for pat in pats:
                    tname = re.split(pat, tname, flags=re.IGNORECASE)[0]

    def _prop_kinship(self):
        my_props = set()

        toSearch = self['firstSentence']

        # don't want lexicon (or a name) to be spotted in the "died on the 3rd with is family"
        toSearch = toSearch.split("died")[0]
        toSearch = toSearch.split("dead")[0]
        toSearch = toSearch.split("killed")[0]
        toSearch = toSearch.split("drowned")[0]

        # their own name might get confusing for this analysis...
        toSearch = toSearch.replace(self["name"], "")

        # intelligent tokenization
        toSearchWords = nlp.word_tokenize( toSearch )

        kinMatch = 0
        kinMatchStronger = 0

        lexicon = nlp.inquirer_lexicon["KIN"]

        for x in toSearchWords:
            if x.upper() in lexicon:
                kinMatch += 1
        for x in nlp.getTuples( toSearchWords, 2, 2 ):
            if x[0].upper() in lexicon and x[1].upper() == "OF":
                kinMatchStronger += 1

        if kinMatch > 0:
            my_props.add("lex_match")
        if kinMatchStronger > 0:
            my_props.add("lex_match_strong")

        # I also need a full name that matches in the last name...
        for names in nlp.getTuples(toSearchWords, 2, 3):
            # must be capitalized...
            if any( x[0].lower() == x[0] for x in names ):
                continue

            # last must be the same name!
            if names[-1].lower() != self["last_name"]:
                continue

            my_props.add("name_match")
            break

        return my_props

    #def _prop_fullBody(self):
    #    fb = re.sub(r"\s+", " ", self['_fullBody'])
    #    fb = fb.strip()
    #    return fb

    def _prop_proper_nouns(self):
        proper_nouns = []

        for chunk in self['spacyFullBody'].noun_chunks:

            #ch = chunk.text
            #ch.replace("\n", " ")
            #ch.replace("  ", " ")
            #ch = ch.strip()

            if chunk.text == chunk.text.lower():
                continue

            # words that aren't spaces...
            chunk = list(chunk)
            chunk = [x for x in chunk if x.pos_ != 'SPACE']

            # expand if necessary
            nextWord = chunk[-1]
            if nextWord.i + 1 < len(nextWord.doc):
                nextWord = nextWord.doc[nextWord.i + 1]

                # if it has capitalization, keep going.
                while str(nextWord).lower() != str(nextWord) or nextWord.pos_ == 'SPACE':
                    # skip spaces...
                    if nextWord.pos_ != 'SPACE':
                        chunk.append(nextWord)

                    if nextWord.i + 1 >= len(nextWord.doc):
                        break

                    nextWord = nextWord.doc[nextWord.i + 1]

            # turn the chunk into a string.
            ch = " ".join([str(w) for w in chunk])

            proper_nouns.append(ch)

        return proper_nouns

    def _prop___extractLexical(self):
        return nlp.extractLexical(self["spacyFullBody"], self["name"])

    def _prop_whatTheyWere(self):
        return self["__extractLexical"]["was"]

    def _prop_whatTheyDid(self):
        return self["__extractLexical"]["did"]

    def _prop_nouns(self):
        doc = self["spacyFullBody"]

        nouns = []
        for x in doc:
            if x.pos_ == "NOUN":
                nouns.append(str(x))
        return nouns

    def _prop_verbs(self):
        doc = self["spacyFullBody"]

        verbs = []
        for x in doc:
            if x.pos_ == "VERB":
                verbs.append(str(x))
        return verbs

    def _prop_OCC(self):

        full_name = self['name']
        def check(s):
            found = []

            s = s.replace(full_name, "")

            words = nlp.word_tokenize(s)
            words = [nlp.lemmatize(x) for x in words]

            sets = set()
            sets.update( nlp.getCloseUnorderedSets(words, minTuple=1, maxTuple=1, maxBuffer=0) )
            sets.update(nlp.getCloseUnorderedSets(words, minTuple=2, maxTuple=2, maxBuffer=1))
            sets.update(nlp.getCloseUnorderedSets(words, minTuple=3, maxTuple=3, maxBuffer=2))
            sets.update(nlp.getCloseUnorderedSets(words, minTuple=4, maxTuple=4, maxBuffer=2))

            for fs in sets:
                if fs in set2code:
                    c = set2code[fs]["code"]

                    found.append({
                        "word": " ".join(fs),
                        "occ": [c],
                        "fs": fs
                    })

            def is_subset_anyone(x):
                for y in found:
                    if x['fs'] != y['fs'] and x['fs'].issubset( y['fs'] ):
                        return True

            found = [x for x in found if not is_subset_anyone(x)]

            return found

        found_first = check(self["firstSentence"].lower())
        found_title = check(self["title"].lower())

        # we want to keep track of "where"
        [ x.update({"where": "firstSentence"}) for x in found_first ]
        [ x.update({"where": "title"}) for x in found_title ]

        return found_first + found_title

    def _OLDER_prop_OCC(self):

        def check(s):
            found = []

            words = nlp.word_tokenize( s.lower() )
            words += ["-"] + nlp.word_tokenize( s.lower() )

            # This algorithm proceeds from largest to smallest tuples, making sure not to count any codes inside codes

            max_tuples = 4
            current_tuples = max_tuples

            process_now = nlp.getTuples( words, minTuple=4, maxTuple=4 )

            while current_tuples > 0:
                # print(process_now, current_tuples)

                dont_process_next = set()

                for tup in process_now:
                    tocheck = " ".join(tup)
                    if tocheck in term2code:
                        c = term2code[tocheck]["code"]
                        found.append({
                            "word": tocheck,
                            "occ": [c]
                        })

                        dont_process_next.update( nlp.getTuples(
                            list(tup),
                            minTuple=current_tuples-1,
                            maxTuple=current_tuples-1
                        ) )

                # print(dont_process_next)

                process_now = set(nlp.getTuples(
                    words,
                    minTuple=current_tuples-1,
                    maxTuple=current_tuples-1
                ))
                process_now = process_now.difference(dont_process_next)

                current_tuples -= 1

            return found

        found_first = check(self["firstSentence"])
        found_title = check(self["title"])

        # we want to keep track of "where"
        [ x.update({"where": "firstSentence"}) for x in found_first ]
        [ x.update({"where": "title"}) for x in found_title ]

        return found_first + found_title

    def _WAIT_prop_OCC_syntax(self):
        coding = self.myCoder
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

        if len(self["name"]) > 0:
            words = wiki.lookupOccupationalTitles(self["name"])
            for x in words:
                lookhimup.update(coding.getOccCodes(x))

            if len(lookhimup) > 0:
                if self.myCoder.debug:
                    g.p("WikiData returns %s which gives OCC %s" % (words, lookhimup))

        if self.myCoder.debug:
            g.p("Extracted name: %s" % self["name"])

        # extract information from the title
        dieWords = ['dies', 'die', 'dead']
        t = self['title']
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

    def _WAIT_prop_OCC_weighted(self):
        fS = self["firstSentence"]
        name = self["name"]

        allCodes = []

        wasDidC = []
        wasDidC += nlp.bagOfWordsSearch(self["whatTheyDid"], term2code)
        wasDidC += nlp.bagOfWordsSearch(self["whatTheyWere"], term2code)

        for x in wasDidC:
            allCodes.append({
                "where": "wasDid",
                "word": x['term'],
                "occ": x['code']
            })

        def justCodes(l):
            return [x['code'] for x in l]

        wasDidC = Counter(justCodes(wasDidC))
        fsC = Counter(justCodes(nlp.tupleBaggerAndSearch(fS, term2code)))
        f500C = Counter(justCodes(nlp.tupleBaggerAndSearch(self['_first500'], term2code)))
        bodyC = Counter(justCodes(nlp.tupleBaggerAndSearch(self['_fullBody'], term2code)))

        weightedC = {}
        w = {}
        w['did'] = 5
        w['fS'] = min(1, 6 * 10. / len(fS)) if len(fS) > 0 else 1
        w['f500'] = 0.5 * 6 * 10. / 500
        w['body'] = min(0.1, 0.1 * 6 * 10. / len(self['_fullBody'])) if len(self['fullBody']) > 0 else 1

        # print w
        for x in set(fsC.keys() + f500C.keys() + bodyC.keys()):
            weightedC[x] = wasDidC[x] * w['did'] + fsC[x] * w['fS'] + f500C[x] * w['f500'] + bodyC[x] * w['body']

        # this is the confidence of our favorite...
        confidence = max(weightedC.values()) if len(weightedC) > 0 else -1

        # order list by the confidences...
        rankedC = sorted(weightedC.items(), key=lambda x: -x[1])

        # and take the top 3
        topC = rankedC[:3]
        topC = [list(x) for x in topC]

        # then idk do something...

    def _prop_gender(self):
        male = nlp.inquirer_lexicon.countWords("MALE", self['fullBody'])
        female = nlp.inquirer_lexicon.countWords("Female", self['fullBody'])

        # if the results are unconclusive from this simple check:
        if male + female < 4 or abs(male - female) / (male + female) < 0.25:
            guess = nlp.gender_detector.get_gender(self["first_name"])
            if guess in ["male","female"]:
                return guess

            # if this even didn't work!
            return "unknown"

        if male > female:
            return "male"
        return "female"

    def _prop_name(self):
        return str(self['spacyName']).strip()

    def _prop_first_name(self):
        return nlp.first_name(self["name"])

    def _prop_last_name(self):
        return nlp.last_name(self["name"])

    def _prop_spacyFullBody(self):
        return nlp.spacy_parse(self['fullBody'])

    def _prop_firstSentence(self):
        return extractFirstSentence(self['fullBody']).strip()

    def _prop_spacyFirstSentence(self):
        return nlp.spacy_parse(self["firstSentence"])

    def _prop_age(self):
        g.p.pdepth = 0

        lastName = self["name"].split()[-1]

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
    #                                                     END PROPERTIES SECTION
    # _----------------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------------

    def codeSummary(self):
        html = """
        <style>
        .code {
            padding: 5px;
            display: inline-block;
            margin: 5px;
            border: 1px solid;
        }
        </style>
        """
        for x in self["OCC"]:
            html += "<div class='code'>"
            for k,v in x.items():
                html += "<b>%s</b> %s <br>" % (k,v)
            html += "</div>"

        return html

    def codedFirstSentenceHtml(self):
        html = self["firstSentence"]

        for x in self['OCC']:
            repl = r"\1<b>\2 (%s)</b>\3" % ",".join(x['occ'])
            html = re.sub( r"([^a-zA-Z]|^)(%s)([^a-zA-Z]|$)" % re.escape(x['word']), repl=repl, string=html )

        return html

    # bag of words approach
    def code(self, coding, toRecode=None):
        assert isinstance(coding, Coder)

        if toRecode is None:
            toRecode = self._get_all_props()

        self.isCoded = True
        self.myCoder = coding

        # we go through and rerun anything in toRecode
        for x in toRecode:
            # simply remove all the attributes that are to be recoded
            # this is necessary, otherwise some codings may rely on past iterations!
            if x in self:
                del self[ x ]

            self[ x ]

        self._clear_spacy_props()

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

    def loadPreviouslyCoded(self, loadDirName, N=None, rand=True):
        from random import shuffle, seed
        from time import time

        import humanize
        import os
        from os import path
        from datetime import datetime

        seed(time())

        loadDir = path.join(path.dirname(__file__), '..', 'codeDumps', loadDirName)

        if not os.path.isdir(loadDir):
            print("Load directory '%s' not found. Please select from the following:" % loadDirName)
            print( ",".join( os.listdir(path.join(path.dirname(__file__), '..', 'codeDumps') ) ) )
            return

        toLoad = os.listdir(loadDir)
        if rand:
            shuffle(toLoad)
        toLoad = toLoad[:N]

        #self.obituaries = []
        new_obituaries = []
        for fn in toLoad:
            relfn = path.join(loadDir, fn)
            d = Doc({"relfn": relfn})
            with open(relfn, 'rb') as thisF:
                d.load(thisF.read())

            new_obituaries.append(d)

        print("Successfully loaded %s documents." % len(new_obituaries))

        self.obituaries.extend(new_obituaries)

        mod_time = os.stat(loadDir).st_mtime
        mod_dt = datetime.fromtimestamp(int(mod_time))
        now_dt = datetime.now()
        time_diff = humanize.naturaldelta(now_dt - mod_dt)

        print("Directory `%s` was last modified %s ago" % (loadDirName, time_diff))

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

            outfn = path.join(dumpDir, "%s.pickle" % d['id'])

            with open( outfn, 'wb' ) as outf:
                outf.write( d.dump() )

    def loadDocs(self, N=None, start=0, rand=True):
        with open(inFn) as inF:
            rows = DictReader(inF)
            rows = g.select(rows, N=N, start=start, rand=rand)

        self.obituaries = [Doc(dict(x)) for x in rows]

    def findObitsByInfo(self, **kwargs):
        found = []
        for d in self.obituaries:
            thisOneSucks = False
            for k in kwargs:
                if not d[ k ] == kwargs[ k ]:
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

    def codeAll(self, toRecode=None, verbose=False):
        from time import time
        from datetime import timedelta

        lastPrintTime = time()
        startTime = time()
        ndocs = len(self.obituaries)

        for index, d in enumerate(self.obituaries):
            if verbose:
                print("coding document %s" % index)

            # every now and then, let us know how it's going!
            if time() - lastPrintTime > 5:
                secondsLeft = int( ( float(ndocs) - index ) * (time() - startTime) / index )
                print("coding document %s/%s. ETA: %s" % (index, ndocs, timedelta(seconds=secondsLeft)))
                lastPrintTime = time()

            d.code(coding=self, toRecode=toRecode)

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
            guesses = list(chain.from_iterable(y['occ'] for y in d['OCC']))
            if len(guesses) == 1:
                OCCsingle.update(guesses)

        # should it be fractional?
        for d in self.obituaries:
            guesses = list(chain.from_iterable(y['occ'] for y in d['OCC']))
            for y in guesses:
                OCCmultiple[y] += 1. / len(guesses)

        # or tuples?
        for d in self.obituaries:
            guesses = list(set(chain.from_iterable(y['occ'] for y in d['OCC'])))
            guesses = tuple(sorted(guesses))
            OCCcomb[guesses] += 1

        OCCgraph = Counter()
        # we could build a graph
        for d in self.obituaries:
            guesses = list(set(chain.from_iterable(y['occ'] for y in d['OCC'])))
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
                    guesses = list(chain.from_iterable(guess['occ'] for guess in doc['OCC']))
                    if len(guesses) == 1 and guesses[0] == occ:
                        w("<p>%s</p>" % doc['spacyFirstSentence'])

    def generateHandCodingSheets_table(self, info=["firstSentence", "guess"], toCode=["OCC"]):
        colNames = info + [ "corrected <b>%s</b>" % x for x in toCode ]

        col_data = 75 / len(info)
        col_input = 25 / len(toCode)

        html = ""

        html += """
        <style>
        .col_data{ width: %s%%; }
        .col_input{ width: %s%%; }
        table {
            border-collapse: collapse;
        }
        td {
            border: 1px solid;
            padding: 7px 17px;
        }
        </style>
        """ % (col_data, col_input)

        html += "<table>"
        html += "<tr>%s</tr>" % "".join( "<td>%s</td>" % x for x in colNames )
        for d in self.obituaries:
            colVals = [d[x] for x in info]
            html += "<tr>%s</tr>" % "".join(
                ["<td class='col_data'>%s</td>" % x for x in colVals] + \
                ["<td class='col_input'></td>" for x in toCode]
            )
        html += "</table>"

        return html

    def generateHandCodingSheets_linear(self, info=["firstSentence", "OCC"], toCode=["OCC"]):
        html = ""

        html += """
        <style>
            td.col_input {
                height: 2em;
            }
            table {
                width: 100%;
            }
            pre {
                white-space: pre-wrap;
                margin: 0.2em;
            }
        </style>
        """

        for d in self.obituaries:
            for x in info:
                html += "<b>%s: </b> <pre>%s</pre>" % (x, d[x])

            html += "<table>"
            html += "<tr>%s</tr>" % "".join("<td><b>%s</b></td>" % x for x in toCode)
            html += "<tr>%s</tr>" % "".join(
                ["<td class='col_input'></td>" for x in toCode]
            )
            html += "</table>"

            html += "<hr>"

        return html


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

def getRandomDocs(num):
    from random import sample
    return sample( allDocs, num )

def regenerateW2C(expandSynonyms = False):
    print("Regenerating W2C correspondence")
    import numpy as np
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
    occ2000Fn = path.join(path.dirname(__file__), "..", "w2c_source", "occ2000 ver 4a2.xls")
    print("Extracting terms from Abdullah's OCC codes file %s" % occ2000Fn)
    workbook = xlrd.open_workbook(occ2000Fn)

    super_wksht = workbook.sheet_by_index(17)

    for row in range(1, 500):
        try:
            code = super_wksht.cell(row, 0).value
        except IndexError:
            break

        term = super_wksht.cell(row, 2).value
        if type(term) == int:
            continue

        term = term.lower()
        terms = term.split("|")

        for term in terms:
            term = term.strip()
            if term == "":
                continue

            codegen.append({
                "term": term,
                "code": "super:%03d" % int(code),
                "source": "occ2000_updated.xls"
            })
            # print((code, term))

    for wksheet_i in list(range(3, 17)) + [18]:
        worksheet = workbook.sheet_by_index(wksheet_i)
        print("Working on worksheet %s" % wksheet_i)

        for row in range(10000):
            #print(row)
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
            if wksheet_i == 18:
                print(terms, code)

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

                try:
                    int(code)
                    codegen.append({
                        "term": term,
                        "code": "%03d" % int(code),
                        "source": "occ2000_updated.xls"
                    })
                except ValueError:
                    if type(code) == str and len(code) and code[0] == "s":
                        print("HERE!")
                        codegen.append({
                            "term": term,
                            "code": code,
                            "source": "occ2000_updated.xls"
                        })



    # my hand-coding
    if False:
        handCFN = path.join(path.dirname(__file__), "..", "w2c_source", "hand-coding.csv")
        with open(handCFN) as handCF:
            for c in DictReader(handCF):
                c['source'] = "hand-coding.csv"
                codegen.append(c)

    if False:
        # all except agent.n.02
        for x in nlp.wn.synset('representative.n.01').hypernyms():
            if x != nlp.wn.synset('agent.n.02'):
                codegen.append({
                    "term": x.name(),
                    "code": "003",
                    "source": "hand-coded-synset"
                })

    if False:
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
    skip = sorted(set([ "%s: %s"% (x['term'],x['code']) for x in codegen if count_terms[ x['term'] ] != 1 ]))
    print("\n".join( skip ))
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
    print( "Reloading 'codes', 'set2code' and 'term2code'..." )
    loadAssociations()

codes = None
term2code = {}
set2code = {}

def loadAssociations():
    global codes
    global term2code
    global set2code

    CSV_fn = path.join(path.dirname(__file__), "..", "w2c_source", "compiledCodes.csv")
    print("Loading term-code associations into variable 'codes' from %s..." % CSV_fn)
    print("Loading term dictionary into variable 'term2code' from %s..." % CSV_fn)

    with open(CSV_fn, 'r') as outCodesF:
        CSV_r = DictReader(outCodesF)
        codes = list(CSV_r)

    for code in codes:
        term2code[ code["term"] ] = code

        words = nlp.word_tokenize( code["term"] )
        words = [nlp.lemmatize(x) for x in words]
        set2code[ frozenset(words) ] = code

loadAssociations()

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

class _keydefaultdict(dict):
    __missing__ = lambda self, key: key

def _codeToName():
    c2n = _keydefaultdict()
    officialTitlesFn = path.join(path.dirname(__file__), '..', 'coding', 'occ2000.officialTitles.csv')
    with open(officialTitlesFn) as officialTitlesF:
        for row in DictReader(officialTitlesF):
            if row['officialTitle'] == "":
                continue

            code = "%03d" % int(row['code'])

            c2n[code] = row['officialTitle']

    return c2n

codeToName = _codeToName()
