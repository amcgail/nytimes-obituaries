import xlrd
import occ
from xlutils.copy import copy
from collections import defaultdict
from itertools import chain
from pprint import pprint
from collections import Counter

c = {
    "title": 6,
    'newId': 9,
    'id': 1,
    'code': 2
}

coding = "v2.0"
id_column = c["newId"]

coder = occ.Coder()
coder.loadPreviouslyCoded(coding)#, N=1, rand=False)

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
    hand_code = set(hand_code)

    id = int(worksheet.cell(i, id_column).value)

    machine_code = coder.findObitByInfo(id=id)['OCC']
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

    counters['total'] += 1
    missed_counter.update(hand_code.difference(machine_code))
    total_counter.update(hand_code)

pprint(dict(counters))
for k in sorted(list(total_counter.keys())):
    print( "%s: missed %s / %s" % (k, missed_counter[k], total_counter[k]))

"""
codingAll
{
 'some disagreement': 525,
 'disagree, but agree on something': 227,
 'disagree, no machine code at all': 200,
 'disagree, on supercode': 66,
 'disagree, only one answer': 315,
 'some agreement': 702,
 'total agreement': 475,
 'total': 1000}
 
v2.0
{
 'disagree, but agree on something': 225,
 'disagree, no machine code at all': 188,
 'disagree, on supercode': 66,
 'disagree, only one answer': 285,
 'machine coded but no hand code': 18,
 'no hand code': 29,
 'some agreement': 703,
 'some disagreement': 511,
 'total agreement': 489,
 'total': 1000,
}

001: missed 44 / 151
001a: missed 12 / 12
002: missed 12 / 20
003: missed 8 / 21
004: missed 0 / 3
005: missed 2 / 4
006: missed 5 / 6
012: missed 5 / 17
013: missed 0 / 1
016: missed 1 / 1
020: missed 1 / 1
021: missed 2 / 5
022: missed 3 / 3
023: missed 11 / 22
030: missed 2 / 2
031: missed 2 / 2
035: missed 5 / 6
041: missed 1 / 6
043: missed 16 / 48
050: missed 2 / 2
062: missed 1 / 1
071: missed 2 / 3
073: missed 0 / 1
080: missed 1 / 1
085: missed 0 / 2
100: missed 1 / 1
102: missed 1 / 1
121: missed 0 / 1
122: missed 1 / 1
123: missed 0 / 1
130: missed 0 / 5
131: missed 1 / 1
132: missed 2 / 2
136: missed 0 / 3
141: missed 2 / 2
144: missed 0 / 1
146: missed 1 / 1
151: missed 1 / 2
154: missed 1 / 1
160: missed 3 / 3
161: missed 3 / 14
164: missed 1 / 3
165: missed 10 / 10
170: missed 3 / 9
171: missed 1 / 1
172: missed 4 / 8
174: missed 1 / 2
180: missed 1 / 3
182: missed 1 / 4
183: missed 0 / 2
186: missed 5 / 24
1a: missed 4 / 4
200: missed 1 / 3
202: missed 1 / 3
204: missed 5 / 29
206: missed 0 / 1
210: missed 7 / 39
211: missed 2 / 15
220: missed 58 / 105
230: missed 1 / 1
231: missed 1 / 1
232: missed 2 / 2
233: missed 0 / 1
234: missed 2 / 2
240: missed 4 / 9
243: missed 0 / 1
255: missed 0 / 1
260: missed 1 / 27
263: missed 7 / 11
270: missed 6 / 49
271: missed 16 / 29
272: missed 15 / 52
274: missed 0 / 18
275: missed 14 / 80
276: missed 2 / 13
280: missed 6 / 18
281: missed 4 / 27
281283: missed 1 / 1
282: missed 1 / 7
283: missed 2 / 18
285: missed 18 / 100
286: missed 1 / 3
291: missed 2 / 10
292: missed 0 / 1
293: missed 1 / 1
305: missed 0 / 1
306: missed 9 / 30
316: missed 0 / 1
371: missed 1 / 3
380: missed 1 / 1
382: missed 4 / 7
395: missed 0 / 1
400: missed 0 / 2
423: missed 0 / 1
425: missed 1 / 1
442: missed 1 / 1
450: missed 0 / 1
454: missed 0 / 1
470: missed 5 / 11
482: missed 4 / 4
492: missed 1 / 2
540: missed 1 / 1
570: missed 1 / 1
605: missed 1 / 1
651: missed 2 / 2
715: missed 1 / 1
721: missed 1 / 1
775: missed 1 / 1
846: missed 1 / 1
980: missed 23 / 23
982: missed 5 / 5
s043: missed 44 / 44
s130: missed 2 / 2
s160: missed 1 / 1
s220: missed 16 / 16
s300: missed 1 / 1
s980: missed 3 / 3
"""