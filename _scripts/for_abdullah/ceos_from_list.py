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

print("Loading documents")

coder.loadPreviouslyCoded("v2.1")

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
    strong_candidates = list(filter( lambda x: x['hn'].first == ceo_name.first, candidates ))

    if not len(strong_candidates):
        continue

    # strongest candidates shouldn't disagree on anything!
    def super_strong_name_match(a, b):
        a, b = a.as_dict(), b.as_dict()
        ks = set(list(a.keys()) + list(b.keys()))

        for k in ks:
            if k not in a or k not in b:
                continue

            if a[k] != '' and b[k] != '':
                if k == 'middle':
                    if len(a[k]) < 3 or len(b[k]) < 3:
                        if a[k][0] == b[k][0]:
                            continue

                if a[k] != b[k]:
                    return False

        return True

    strongest_candidates = list(filter( lambda x: super_strong_name_match(x['hn'], ceo_name), candidates))

    if not len(strongest_candidates):
        continue

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