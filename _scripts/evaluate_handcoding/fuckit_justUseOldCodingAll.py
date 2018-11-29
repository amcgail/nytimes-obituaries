import xlrd
import occ
from xlutils.copy import copy
from collections import defaultdict
from itertools import chain

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll")#, N=1, rand=False)

infn = "/home/alec/projects/nytimes-obituaries/hand_coding_originals/hand coding ds as combined sample aug 24.xlsx"

workbook = xlrd.open_workbook(infn)
worksheet = workbook.sheet_by_index(0)

c = {
    "title": 6,
    'newId': 9,
    'id': 1,
    'code': 2
}

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

for i in range(1, 1001):
    if i % 50 == 0:
        print("finished with ", i, "... getting tired")

    hand_code = worksheet.cell(i, c['code']).value

    if type(hand_code) == str:
        hand_code = [ canonicalize(x) for x in  hand_code.split(",") ]
    else:
        hand_code = [canonicalize(hand_code)]
    hand_code = set(hand_code)

    id = int(worksheet.cell(i, c['id']).value)

    machine_code = coder.findObitByInfo(id=id)['OCC']
    machine_code = list( chain.from_iterable( [x['occ'] for x in machine_code] ) )
    machine_code = set(machine_code)

    agreement = machine_code.intersection( hand_code )
    disagreement = machine_code.symmetric_difference( hand_code )

    if len(agreement):
        counters['some_agreement'] += 1
    if machine_code == hand_code:
        counters['total_agreement'] += 1
    if not len(machine_code):
        counters['no code at all'] += 1
    if machine_code != hand_code:
        counters['disagreement'] += 1

    counters['total'] += 1

print(counters)