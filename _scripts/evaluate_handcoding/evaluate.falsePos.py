# ---------- IMPORTS -----------

import xlrd
import occ
from xlutils.copy import copy
from collections import defaultdict
from itertools import chain
from pprint import pprint
from collections import Counter
import os
import csv

# -----------  ARGUMENTS ------------

handCodingFn = "/home/alec/projects/nytimes-obituaries/hand_coding_originals/hand coding ds as combined sample aug 24.xlsx.xlsx.xlsx"
name = "appos"
coding = "v2.1"
agg_supergroups = False
recodeWhileDoingIt = True

# -----------  INITIALIZATION ------------

fileName = name
if agg_supergroups:
    fileName += ".supergroups"
fileName += ".csv"
outCSV = os.path.join( os.path.dirname(__file__), "..", "..", "exports", fileName )

supergroups = {
    "s043": [2] + list(range(4,44)),
    "s050": range(50,74),
    "s080": range(80,96),
    "s100": range(100,125),
    "s130": range(131, 154),
    "s160": range(160, 197),
    "s200": range(200, 207),
    "s210": range(210, 216),
    "s220": range(220, 235),
    "s260": range(260, 297),
    "s300": range(300, 355),
    "s360": range(360, 366),
    "s370": range(370, 396),
    "s400": range(400, 417),
    "s420": range(420, 426),
    "s430": range(430, 466),
    "s470": range(470, 497),
    "s500": range(500, 594),
    "s600": range(600, 614),
    "s620": range(620, 677),
    "s680": range(680, 695),
    "s700": range(700, 763),
    "s770": range(770, 897),
    "s900": range(900, 976),
    "s980": range(980, 984),
    "s992": [992]
}

c = {
    "title": 6,
    'newId': 9,
    'id': 1,
    'code': 2
}

id_column = c["newId"]

coder = occ.Coder()
coder.loadPreviouslyCoded(coding)#, N=1, rand=False)

obits_by_id = {
    x['id']: x
    for x in coder.obituaries
}

workbook = xlrd.open_workbook(handCodingFn)
worksheet = workbook.sheet_by_index(0)

def canonicalize(x):
    if type(x) == str:
        try:
            x = int(x)
        except ValueError:
            return x
    if type(x) in [int, float]:
        x = "%03d" % int(x)
        return x

def get_supergroup(x):
    if not len(x):
        return x

    if x[0] == "s":
        return x

    try:
        z = int(x)
        for k in supergroups:
            if z in supergroups[k]:
                return k
    except ValueError:
        pass

    if x == "001a":
        x = "001"
    return "s^%s" % x
    raise Exception("%s not found" % x)

counters = defaultdict(int)
total_counter = Counter()
missed_counter = Counter()
false_pos_counter = Counter()

#for i in range(1, 101):
for i in range(1, 1001):
    if i % 50 == 0:
        print("finished with ", i, "... getting tired")

    hand_code = worksheet.cell(i, c['code']).value

    if type(hand_code) == str:
        hand_code = [ canonicalize(x) for x in  hand_code.split(",") ]
    else:
        hand_code = [canonicalize(hand_code)]
    hand_code = [x.strip() for x in hand_code]

    if agg_supergroups:
        hand_code = [get_supergroup(x) for x in hand_code]

    hand_code = [x for x in hand_code if x != ""]

    def fix001a(x):
        if x == "001a":
            return "001"
        return x

    hand_code = map(fix001a, hand_code)
    hand_code = set(hand_code)

    id = int(worksheet.cell(i, id_column).value)

    obit = obits_by_id[ id ]
    if 'spacyName' in obit._prop_cache:
        del obit['spacyName']
    machine_code = obit._OCC_just_appos()
    #if recodeWhileDoingIt:
    #    del obit['OCC']
    #machine_code = obit['OCC']
    machine_code = list( chain.from_iterable( [x['occ'] for x in machine_code] ) )
    if agg_supergroups:
        machine_code = [get_supergroup(x) for x in machine_code]
    machine_code = set(machine_code)

    if False:
        print( hand_code )
        print( machine_code )

    agreement = machine_code.intersection( hand_code )
    disagreement = machine_code.symmetric_difference( hand_code )

    if len(agreement):
        counters['some agreement'] += 1
    if machine_code == hand_code:
        counters['total agreement'] += 1
    if len(disagreement):
        counters['some disagreement'] += 1

        if any("s" in x for x in disagreement):
            counters['disagree, on supercode'] += 1

        if len(hand_code) == 1:
            counters['disagree, only one answer'] += 1

        if len(agreement):
            counters['disagree, but agree on something'] += 1

        if not len(machine_code):
            counters['disagree, no machine code at all'] += 1

    if (not len(hand_code)) and len(machine_code):
        counters['machine coded but no hand code'] += 1

    if (not len(hand_code)):
        counters['no hand code'] += 1

    if len(machine_code - hand_code):
        counters['false positives'] += 1

    counters['total'] += 1
    false_pos_counter.update(machine_code - hand_code)
    missed_counter.update(hand_code.difference(machine_code))
    total_counter.update(hand_code)

if False:
    pprint(dict(counters))
    for k in sorted(list(total_counter.keys())):
        print( "%s: missed %s / %s" % (k, missed_counter[k], total_counter[k]))

def get_metric(k):
    t = total_counter[k]
    fp = false_pos_counter[k]
    m = missed_counter[k]
    hit = t - m

    if fp == 0:
        return "inf"

    return "%.03f" % (hit / fp)



if False:
    # write the shit to an excel file, instead of a CSV

    workbook   = xlsxwriter.Workbook('filename.xlsx')

    worksheet1 = workbook.add_worksheet()
    worksheet1.write_string(row, col, string)

with open(outCSV, "w") as csvf:
    csvw = csv.writer(csvf)
    all_keys = sorted(total_counter.keys())
    csvw.writerow(
        "OCC,missed,hit,pctHit,falsePos,total,howgood".split(",")
    )
    for k in all_keys:
        csvw.writerow([
            k,
            missed_counter[k],
            total_counter[k] - missed_counter[k],
            float(total_counter[k] - missed_counter[k]) / total_counter[k],
            false_pos_counter[k],
            total_counter[k],
            get_metric(k)
        ])