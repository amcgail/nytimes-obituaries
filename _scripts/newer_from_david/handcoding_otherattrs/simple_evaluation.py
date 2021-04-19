import os
from collections import defaultdict, Counter
from operator import attrgetter
from os import path
import xlrd
from nltk import edit_distance

sourcedir = path.join( path.dirname(__file__), "..", "..", "hand_coding_originals", "hand coding group March 28" )
files = os.listdir( sourcedir )

rows = []
keys = ["education", "religion", "honorific title", "name", "occ group", "job", "ind", "race", "ethnicity", "born", "lived", "died", "citizen"]

for fn in files:
    if fn[-4:] != "xlsx":
        continue

    print("Parsing",fn)

    workbook = xlrd.open_workbook( path.join(sourcedir,fn) )
    worksheet = workbook.sheet_by_index(0)

    all_rows = list(worksheet.get_rows())
    head, myrows = all_rows[0], all_rows[1:]

    head = list(map( attrgetter("value"), head ))
    myrows = [
        list(map(str, map(attrgetter("value"), x)))
        for x in myrows
    ]

    myrows = [
        {
            head[i]: row[i]
            for i in range(len(row))
        }
        for row in myrows
    ]

    rows += myrows

print("Found columns", head)

byid = defaultdict(list)
for row in rows:
    byid[ row['id1'] ].append( row )

matched_none = 0

mismatch_overview = ""

mismatch_counter = Counter()
notblank_counter = Counter()

for id in byid:


    matched = 0

    mismatches = []

    for key in ["education", "religion", "honorific title", "name", "occ group", "job", "ind", "race", "ethnicity",
                "born", "lived", "died", "citizen"]:

        #if key not in byid[id]:
        #    print("%s: not found" % key)
        #    continue


        vals = [ x[key] for x in byid[id] if key in x ]
        if len(vals) < 2:
            break

        vals = [ x if x != '.' else '' for x in vals ]

        match = True
        for i, x in enumerate(vals):
            for y in vals[i+1:]:
                if edit_distance(x.lower(), y.lower()) > 4:
                    match = False

        if key in ['ind','occ group']:
            if len(set( map(str.strip,map(str.lower, vals)) )) > 1:
                match = False
            else:
                match = True

        if not match:
            mismatches.append( "%s: %s" % (key, vals) )
            mismatch_counter.update([key])
        else:
            matched += 1

        if not all(x=='' for x in vals):
            notblank_counter.update([key])


    if matched == 0:
        matched_none += 1
    else:
        mismatch_overview += "## ID: %s\n\n" % byid[id][0]['id2']
        mismatch_overview +=  "\n".join( "+ %s" % x for x in mismatches )  + "\n"
        mismatch_overview += "+ (%s attributes matched)\n\n" % matched

        #mismatch_overview += "\n>\n"
        #mismatch_overview += byid[id][0]['fullBody'] + "\n\n"

print("## Overview")
print("+ %s matched none!" % matched_none)
print(mismatch_overview)

print("Key overview")
for key, count in mismatch_counter.items():
    print("+ %s: %0.2f%% (%s / %s which weren't blank) missed" % (key, 100*count/notblank_counter[key], count, notblank_counter[key]))


print( byid["38700.0"][0]['title'] )