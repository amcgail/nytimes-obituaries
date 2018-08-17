from collections import defaultdict
import occ
import datetime

from pymongo import MongoClient
db = MongoClient()['occ_coding']

missedTags = defaultdict(str)

class CannotBeParsed(Exception):
    pass

class Doc:
    def __init__(self, parseunit, fulltext):
        self.parseunit = parseunit
        self.fulltext = fulltext
        self.parts = {}

    def parse(self):
        self.extract_attributes()
        self.fix_attributes()

    def fix_attributes(self):
        import re

        for p, v in self.parts.items():
            # get rid of newlines
            v = "".join( re.split("[\r\n]", v) )
            self.parts[p] = v

        paras = re.split("[\r\n]{4}", self.body)
        paras = [ "".join(re.split("[\r\n]", x)) for x in paras ]
        self.body = "\n\n".join(paras)

    def extract_attributes(self):
        global missedTags

        import re

        date = ''
        name = ''
        title = ''
        monthlist = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                     "November", "December"]

        attributes = ["CORRECTION-DATE", "CORRECTION", "CATEGORY","URL","TITLE","ORGANIZATION","NAME", "LOAD-DATE", "GRAPHIC", "SECTION","LENGTH","TICKER","INDUSTRY","COUNTRY","STATE","CITY","COMPANY","GEOGRAPHIC","SUBJECT","PERSON","LANGUAGE","TYPE"]
        reAllAttr = "(%s):" % "|".join(attributes)

        ###############################
        ##Let's get the person's name
        ###############################
        fullThing = self.fulltext
        head = re.split(reAllAttr, fullThing)[0]

        self.head = head
        title = re.split("[0-9]+ of [0-9]+ DOCUMENTS", head)
        if len(title) < 2:
            # print(fullThing, self.parseunit.fn)
            raise CannotBeParsed()
        title = title[1]
        title = " ".join(title.split("\n")[3:])
        self.title = title.strip()

        self.name = re.split(r'[`\=~!@#$%^&*()_+\[\]{};\'\\:"|<,/<>?]', title)[0]

        ###############################
        ## Let's get the dateline and the date only
        ###############################
        headList = head.split("\n")
        newheadList = []
        for i in headList:
            newheadList.append(i.strip())
        # print(newheadList)

        for i in newheadList:
            if len(i) > 1:
                parsed = i.split()
                x = parsed[0]
                if x in monthlist:
                    dateline = i

        # print(dateline)
        dateJoin = "|".join([x.lower() for x in monthlist])
        dateJoin = "(%s)" % dateJoin
        finddate = re.search(r'(%s\s+\d+\,\s+\d+)' % dateJoin, head.lower())
        self.date = finddate.group(1)

        if False:
            try:
                (beforeBody, body, afterBody) = re.split("[\n\r]{6}", fullThing)
            except ValueError:
                print(fullThing)
                raise Exception("Didn't find the three sections")

        body = None

        findAllTags = list(re.finditer(reAllAttr, fullThing))
        for i, tag in enumerate(findAllTags):
            name = fullThing[ tag.span()[0] : tag.span()[1] ]
            name = name.strip().split(":")[0]

            if i < len(findAllTags) - 1:
                val = fullThing[ tag.span()[1] : findAllTags[i+1].span()[0] ]
            else:
                val = fullThing[ tag.span()[1] : ]

            val = val.strip()

            if name in ["BYLINE","DATELINE","LENGTH"]:
                findBody = re.split("[\r\n]{4,8}", val)
                if len(findBody) > 1:
                    val = findBody[0]
                    body = "\r\n\r\n\r\n".join( findBody[1:] )

            if False:
                # useful for locating tags we missed
                findOtherTags = re.findall("^[A-Z]{3,}:", val)
                if len(findOtherTags):
                    for x in findOtherTags:
                        missedTags[x] = (name, val)

            self.parts[name] = val

        if body is None:
            print(self.fulltext)
            raise Exception("Body was none")

        self.body = body

class ParseUnit:
    def __init__(self, fn):
        self.fn = fn
        self.docs = []

    def grab_from_disk(self):
        import codecs
        with codecs.open(self.fn, 'r', "ISO-8859-1") as infile:
            self.full = infile.read()

    def extract_docs(self):
        import re

        # remove all UTF characters
        all = self.full
        all = "".join([c for c in self.full if ord(c) < 128])

        docs = re.split("\s*Copyright [0-9]{4} The New York Times Company\s*", all)
        print("Extracted %d docs from '%s'" % (len(docs), self.fn))

        self.docs = [Doc(self, x) for x in docs]

    def extract_from_docs(self):
        to_delete = []
        for i,d in enumerate(self.docs):
            try:
                d.parse()

                #print(d.parts)
                #print(d.body)
            except CannotBeParsed:
                to_delete.append(i)

        self.docs = [ d for i,d in enumerate(self.docs) if i not in to_delete ]

    def extract(self):
        self.grab_from_disk()
        self.extract_docs()
        self.extract_from_docs()

class Extractor:
    def __init__(self, sourcedir):
        self.sourcedir = sourcedir
        self.docs = []

    def extract(self):
        import os
        from os import path
        import numpy as np

        allNonUTFChars = set()

        for f in os.listdir(self.sourcedir)[:10]:
            self.docs.append( ParseUnit( path.join(self.sourcedir, f) ) )

        for d in self.docs:
            d.extract()


extractor = Extractor("../allobitmainfiles")
extractor.extract()

if False:
    # for debugging
    with open("test_obit_extract.txt", "w") as outf:
        for x in extractor.docs:
            for y in x.docs:
                outf.write("-----------------------\n\n")
                outf.write("---------BODY:----------\n\n")
                outf.write(y.body)
                #outf.write("\n\n---------ORIG:----------\n\n")
                #outf.write(y.fulltext)
                #outf.write("\n".join("%s: %s" % (k,v) for k,v in y.parts.items()))
                outf.write("\n\n")

docs = [ y for x in extractor.docs for y in x.docs ]

coder = occ.Coder()
for d in docs:
    assert(isinstance(d, Doc))

    docinfo = {
        "nyt_%s" % k: v
        for k, v in d.parts.items()
    }
    docinfo['fullBody'] = d.body
    docinfo['originalFile'] = d.parseunit.fn

    doc = occ.Doc()
    doc._prop_cache = docinfo

    coder.obituaries.append(doc)


coder.dumpCodes("all_v2.0")