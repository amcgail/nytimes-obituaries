import xlrd
import occ
from xlutils.copy import copy
from collections import defaultdict
from itertools import chain
from pprint import pprint
from collections import Counter
import os
import csv

outCSV = os.path.join( os.path.dirname(__file__), "../../exports/coding_eval.csv" )

c = {
    "title": 6,
    'newId': 9,
    'id': 1,
    'code': 2
}

coding = "v2.1"
id_column = c["newId"]

coder = occ.Coder()
coder.loadPreviouslyCoded(coding)#, N=1, rand=False)

obits_by_id = {
    x['id']: x
    for x in coder.obituaries
}

infn = "/home/alec/projects/nytimes-obituaries/hand_coding_originals/hand coding ds as combined sample aug 24.xlsx.xlsx.xlsx"

workbook = xlrd.open_workbook(infn)
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
    hand_code = [x for x in hand_code if x != ""]

    def fix001a(x):
        if x == "001a":
            return "001"
        return x

    hand_code = map(fix001a, hand_code)
    hand_code = set(hand_code)

    id = int(worksheet.cell(i, id_column).value)

    machine_code = obits_by_id[ id ]['OCC']
    machine_code = list( chain.from_iterable( [x['occ'] for x in machine_code] ) )
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

with open(outCSV, "w") as csvf:
    csvw = csv.writer(csvf)
    all_keys = sorted(total_counter.keys())
    csvw.writerow("OCC,missed,falsePos,total,howgood".split(","))
    for k in all_keys:
        csvw.writerow([
            k,
            missed_counter[k],
            false_pos_counter[k],
            total_counter[k],
            get_metric(k)
        ])