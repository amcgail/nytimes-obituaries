#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 12:57:10 2018

@author: alec
"""

import csv
import pprint
import re
from collections import Counter
from csv import DictReader, DictWriter
from csv import reader
from itertools import chain, groupby
from os import path, remove

import xlrd

import g
import nlp
import env


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

class Obituary:
    def __init__(self, init_info={}):
        # the info it's initialized with has "_" before it, so everything on top is coded.
        init_info = {
            "_%s"%k : v
            for k,v in init_info.items()
        }
        self._prop_cache = init_info

        self.isCoded = False
        self.myCoder = None

    def destroy_in_memory(self):
        remove(self['_relfn'])

    def to_pickle(self):
        if not self.isCoded:
            raise Exception("Cannot dump what's not been coded!")

        import pickle

        d = {
            k:v
            for k,v in self._prop_cache.items()
            if not _problematic_for_pickling(v)
        }

        return pickle.dumps(d)

    def from_pickle(self, d, attrs=None):
        import pickle
        d = pickle.loads(d)

        # filter the dictionary, if that's what you ask for
        if attrs is not None:
            d = dict( (k,v) for (k,v) in d.items() if k in attrs )

        self._prop_cache.update(d)

        self.isCoded = True

    def __str__(self):
        return self['firstSentence']

    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    #           This section defines all the functionality of this object as a picklable dictionary
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------
    # _----------------------------------------------------------------------------------------------------------

    def __getitem__(self, item):
        if item in self._prop_cache:
            return self._prop_cache[item]

        """
        else:
            raise AttributeError("%s not loaded for obituary with info: %s" % (
                item,
                pprint.pformat(self._prop_cache, indent=2)
            ))
        """

        """
        we need to calculate it when it wasn't loaded
        """

        #assert(isinstance(self.myCoder, Coder))

        # these have already been automatically extracted by the coder from the attributes folder
        if item not in attributeCoders:
            raise Exception("%s not loaded and we don't know how to create it" % item)

        prop = attributeCoders[item]( self )
        assert(isinstance(prop, g.SingleAttributeCoder))

        val = prop.run()
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
    def code(self, toRecode=None):
        if toRecode is None:
            toRecode = self._get_all_props()

        self.isCoded = True

        # we go through and rerun anything in toRecode
        for x in toRecode:
            # simply remove all the attributes that are to be recoded
            # this is necessary, otherwise some codings may rely on past iterations!
            if x in self:
                del self[ x ]

            self[ x ]

        self._clear_spacy_props()



def codeAll(loadDirName, toRecode=None, debug=False, N=None):
    # depreciated
    import warnings
    warnings.warn("deprecated", DeprecationWarning)

    from time import time

    import os
    from os import path
    from datetime import timedelta

    loadDir = path.join(env.codeDumpDir, loadDirName)

    if not os.path.isdir(loadDir):
        print("Load directory '%s' not found. Please select from the following:" % loadDirName)
        print(",".join(os.listdir(env.codeDumpDir)))
        return

    toLoad = os.listdir(loadDir)
    if N is not None:
        toLoad = toLoad[:N]


    lastPrintTime = time()
    startTime = time()
    ndocs = len(toLoad)

    # actually loads the thing from DB or File or WE
    for index, fn in enumerate(toLoad):

        # every now and then, let us know how it's going!
        if time() - lastPrintTime > 5:
            secondsLeft = int( ( float(ndocs) - index ) * (time() - startTime) / index )
            print("coding document %s/%s. ETA: %s" % (index, ndocs, timedelta(seconds=secondsLeft)))
            lastPrintTime = time()

        relfn = path.join(loadDir, fn)
        d = Obituary({"relfn": relfn})
        with open(relfn, 'rb') as thisF:
            # loads everything
            d.from_pickle(thisF.read(), attrs=None)

        d.code(toRecode=toRecode)

        # now press it back into a pickle!
        if not debug:
            with open(relfn, "wb") as pf:
                pf.write(d.to_pickle())

    print("Successfully coded %s documents." % len(toLoad))

attributeCoders = {}
def _loadAttributes():
    global attributeCoders
    from os import listdir
    from importlib import import_module
    import inspect

    attributesDir = path.join( path.dirname(__file__), "attributes" )

    for fn in listdir(attributesDir):
        print("Parsing file",fn)
        name = ".".join(fn.split(".")[:-1])
        if name == "":
            continue

        module = import_module("attributes.%s" % name)

        classesWithin = inspect.getmembers(module, inspect.isclass)
        for cname, c in classesWithin:
            # print("Found attribute", cname)
            attributeCoders[cname] = c
_loadAttributes()

def attributeNames():
    """
    This boy gives all the codable attributes defined in view of the coders..
    It checks the subclasses of the values inside "attributeCoders", and returns names.

    :return:
    """
    return [ k for k,v in attributeCoders.items() if issubclass(v, g.PropertyCoder) ]

def attributeDocumentation( attrName ):
    return attributeCoders[attrName].__doc__

#from pymongo import MongoClient
#attributeDb = MongoClient()['nytimes_obituaries']['coded_attributes']

class Coder:
    def __init__(self, debug=False, mode="firstSentence"):
        self.debug = debug

        # Initialize a bunch of variables
        self.allResults = []
        self.obituaries = []
        self.stateCounter = Counter()
        self.specificCounters = {}

    """
    def codeAttrsIntoMongo(self, attrs):

        from time import time
        from datetime import timedelta

        lastPrintTime = time()
        startTime = time()
        ndocs = len(self.obituaries)

        # code all the obits
        for index, obit in enumerate(self.obituaries):
            assert (isinstance(obit, Obituary))

            # every now and then, let us know how it's going!
            if time() - lastPrintTime > 5:
                secondsLeft = int( ( float(ndocs) - index ) * (time() - startTime) / index )
                print("coding document %s/%s. ETA: %s" % (index, ndocs, timedelta(seconds=secondsLeft)))
                lastPrintTime = time()

            for attr in attrs:
                if attr not in attributeCoders:
                    raise Exception("Attribute %s not in available coders" % attr)

                c = attributeCoders[attr]

                if not issubclass(c, g.PropertyCoder):
                    raise Exception("Attribute %s is just a helper..." % attr)

                if attr in list(obit.keys()):
                    del obit[attr]

                coding_result = obit[attr]

        print("Done coding documents... dumping to Mongo")

        self.dumpCodesMongo()

    def codeAllIntoMongo(self):

        from time import time
        from datetime import timedelta

        lastPrintTime = time()
        startTime = time()
        ndocs = len(self.obituaries)

        # code all the obits
        for index, obit in enumerate(self.obituaries):
            assert (isinstance(obit, Obituary))

            # every now and then, let us know how it's going!
            if time() - lastPrintTime > 5:
                secondsLeft = int( ( float(ndocs) - index ) * (time() - startTime) / index )
                print("coding document %s/%s. ETA: %s" % (index, ndocs, timedelta(seconds=secondsLeft)))
                lastPrintTime = time()

            for cname, c in attributeCoders.items():

                # skip silly shit
                if not issubclass(c, g.PropertyCoder):
                    continue

                if cname in list(obit.keys()):
                    del obit[cname]

                coding_result = obit[cname]

        print("Done coding documents... dumping to Mongo")

        self.dumpCodesMongo()

    def dumpCodesMongo(self):
        from datetime import datetime
        from time import time
        from datetime import timedelta

        lastPrintTime = time()
        startTime = time()
        ndocs = len(self.obituaries)

        attributeDb.drop()

        codingTime = datetime.now()

        bulkop = attributeDb.initialize_ordered_bulk_op()
        for index, obit in enumerate(self.obituaries):
            assert(isinstance(obit, Obituary))
            # print(obit['id'])


            # every now and then, let us know how it's going!
            if time() - lastPrintTime > 5:
                secondsLeft = int( ( float(ndocs) - index ) * (time() - startTime) / index )
                print("coding document %s/%s. ETA: %s" % (index, ndocs, timedelta(seconds=secondsLeft)))
                lastPrintTime = time()


            accounted_for = set()

            for cname, c in attributeCoders.items():
                accounted_for.add(cname)

                #print(c)
                # skip silly shit
                if not issubclass(c, g.PropertyCoder):
                    continue

                # note that I'm just using whatever's here --
                # this could well be stale if one isn't careful
                coding_result = obit[cname]
                #print("coded", cname, "as")
                #print(coding_result)

                if False:
                    pprint.pprint({
                        "key": cname,
                        "value": coding_result,
                        "obit": obit['id'],
                        "whenCoded": codingTime
                    })

                retval = bulkop.insert({
                    "key": cname,
                    "value": coding_result,
                    "obit": obit['id'],
                    "whenCoded": codingTime
                })

                #print("cname:",cname)

            # and of course the leftovers that weren't generated
            for key, value in obit._prop_cache.items():
                if key in accounted_for:
                    continue

                #print("key:",key)

                retval = bulkop.insert({
                    "key": key,
                    "value": value,
                    "obit": obit['id'],
                    "whenCoded": -1
                })

        retval = bulkop.execute()
    
    def loadFromMongoAttributes(self, attrs_all_obits):
        ""(")
        Loads data from a Mongo query returning objects of form
            {
                "key": _,
                "value": _,
                "obit": _,
                "whenCoded": _
            }
        :param attrs_all_obits:
        :return:
        ""(")

        for obit_id, attrs_this_obit in groupby(attrs_all_obits, lambda attr_info: attr_info["obit"]):
            attrs = {}
            for key, codings in groupby(attrs_this_obit, lambda x: x["key"]):
                most_recent_coding = min( codings, key=lambda x: x['whenCoded'] )
                attrs[ key ] = most_recent_coding['value']

            new_obituary = Obituary()
            new_obituary._prop_cache = attrs
            new_obituary.myCoder = self
            self.obituaries.append(new_obituary)
    """

    def loadPreviouslyCoded(self, loadDirName, N=None, rand=True, attrs=None):
        # depreciated
        import warnings
        warnings.warn("deprecated", DeprecationWarning)


        from random import shuffle, seed
        from time import time

        import humanize
        import os
        from os import path
        from datetime import datetime

        seed(time())

        loadDir = path.join(env.codeDumpDir, loadDirName)

        if not os.path.isdir(loadDir):
            print("Load directory '%s' not found. Please select from the following:" % loadDirName)
            print( ",".join( os.listdir( env.codeDumpDir ) ) )
            return

        toLoad = os.listdir(loadDir)
        if rand:
            shuffle(toLoad)
        toLoad = toLoad[:N]

        # actually loads the thing from DB or File or WE
        #self.obituaries = []
        new_obituaries = []
        for fn in toLoad:
            relfn = path.join(loadDir, fn)
            d = Obituary({"relfn": relfn})
            d.myCoder = self
            with open(relfn, 'rb') as thisF:
                d.from_pickle(thisF.read(), attrs=attrs)

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
            assert(isinstance(d, Obituary))

            outfn = path.join(dumpDir, "%s.pickle" % d['id'])

            with open( outfn, 'wb' ) as outf:
                outf.write(d.to_pickle())

    def loadDocs(self, N=None, start=0, rand=True):
        with open(inFn) as inF:
            rows = DictReader(inF)
            rows = g.select(rows, N=N, start=start, rand=rand)

        self.obituaries = [Obituary(dict(x)) for x in rows]

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


def getRandomDocs(num):
    from random import sample
    return sample( allDocs, num )

def regenerateW2C(expandSynonyms = False):
    print("Regenerating W2C correspondence")
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

    if False:
        # parsing the super worksheet separately from others --
        super_wksht = workbook.sheet_by_index(18)

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

def nice_occ(nasty_occ):
    return set(chain.from_iterable( x['occ'] for x in nasty_occ ))