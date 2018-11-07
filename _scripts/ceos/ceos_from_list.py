from functools import partial

import xlrd
from collections import defaultdict
from nameparser import HumanName
from os import path
import csv


outfn = "extracted_ceos.csv"
outputdir = path.join(path.dirname(__file__), "..", "..", "exports")

ceos_list_fn = "process1996.xlsx"

workbook = xlrd.open_workbook(ceos_list_fn)
worksheet = workbook.sheet_by_index(0)

import occ
coder = occ.Coder()

# ------------ LOAD DOCS -------------------
print("Loading documents")

coder.loadPreviouslyCoded("v2.1")

# ------------ PARSE THE SHIT --------------
print("Generating the last name dictionary")

lastNameToObits = defaultdict(list)
for obit in coder.obituaries:
    obit['hn'] = HumanName( obit['name'] )

    lastNameToObits[ obit['hn'].last ].append( obit )

rows = []

for i in range(497):
    name_str = worksheet.cell(i, 3).value
    ceo_name = HumanName( name_str )


    candidates = lastNameToObits[ ceo_name.last ]

    def isMatch(obit):
        a = obit['hn']
        b = ceo_name

        # first names have to equal exactly
        if a.first != b.first:
            return False

        # last names have to equal exactly
        if a.last != b.last:
            return False

        # middle names are more complicated
        am = a.middle
        bm = b.middle
        if len(am) and len(bm):

            if len(am) <= 2 or len(bm) <=2:
                # am or bm are initials
                if am[0] != bm[0]:
                    # initial and name/initial don't match
                    return False
            else:
                # both am and bm aren't middle initials
                if am != bm:
                    return False

        return True

    strong_candidates = list(filter(isMatch, candidates))

    for c in strong_candidates:
        rows.append({
            "id":c['id'],
            "date":str(c['date']),
            "title":c['title'],
            "firstSentence":c['firstSentence'],
            "ceoName": name_str,
            "obitName": c['name']
        })

    if False:
        print("(%s)" % i)
        print( "Looking for %s" % name_str )
        print("Last name", ceo_name.last)
        print( "Found strong: ", [x['name'] for x in strong_candidates] )
        print( "Found strongest: ", [x['name'] for x in strongest_candidates] )

with open(path.join(outputdir, outfn), 'w') as outf:
    csvw = csv.DictWriter(outf, "id,date,ceoName,obitName,title,firstSentence".split(","))
    csvw.writerows(rows)