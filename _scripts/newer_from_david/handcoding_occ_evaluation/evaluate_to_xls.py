from _csv import writer

import xlrd
import xlwt

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

coding = "v2.1"
id_column = c["newId"]

#coder = occ.Coder()
#coder.loadPreviouslyCoded(coding)#, N=1, rand=False)
#
#obits_by_id = {
#    x['id']: x
#    for x in coder.obituaries
#}

infn = "/home/alec/amcgail2@gmail.com/projects/nytimes-obituaries/hand_coding_originals/hand coding ds as combined sample aug 24.xlsx.xlsx.xlsx"

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


counters = defaultdict(lambda: defaultdict(int))
total_counter = defaultdict(lambda: Counter())
missed_counter = defaultdict(lambda: Counter())
didntcode_counter = defaultdict(lambda: Counter())
didcode_counter = defaultdict(lambda: Counter())
shot_and_missed = defaultdict(lambda: Counter())

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

    occs = ['OCC', 'OCC_syntax', 'OCC_title', 'OCC_wikidata']

    all_machine_code = occ.obitFromId("v2.1", id=id, attrs=occs)

    for machine_code_name in occs:

        machine_code = all_machine_code[machine_code_name]

        # process the machine code to a standard format
        if machine_code == None:
            machine_code = set()
        elif type(machine_code) == list:

            if len(machine_code) and type(machine_code[0]) == dict:
                machine_code = list(chain.from_iterable(x['occ'] for x in machine_code))
            # what!?!?          this exists!?!?
            elif len(machine_code) and type(machine_code[0]) == list:
                machine_code = list( chain.from_iterable( chain.from_iterable(x['occ'] for x in y) for y in machine_code) )
            print("turning into set...", machine_code)
            machine_code = set(machine_code)
        elif type(machine_code) == str:
            machine_code = {machine_code}
        else:
            raise Exception("WTF is this...", machine_code)

        agreement = machine_code.intersection( hand_code )
        disagreement = machine_code.symmetric_difference( hand_code )

        if len(agreement):
            counters[machine_code_name]['some agreement'] += 1
        if machine_code == hand_code:
            counters[machine_code_name]['total agreement'] += 1
        if len(disagreement):
            counters[machine_code_name]['some disagreement'] += 1

            if any("s" in x for x in disagreement):
                counters[machine_code_name]['disagree, on supercode'] += 1

            if len(hand_code) == 1:
                counters[machine_code_name]['disagree, only one correct answer'] += 1

            if len(agreement):
                counters[machine_code_name]['disagree, but agree on something'] += 1

            if not len(machine_code):
                counters[machine_code_name]['disagree, no machine code at all'] += 1

        if (not len(hand_code)) and len(machine_code):
            counters[machine_code_name]['machine coded but no hand code'] += 1

        if (not len(hand_code)):
            counters[machine_code_name]['no hand code'] += 1

        counters[machine_code_name]['total # obits'] += 1
        missed_counter[machine_code_name].update(hand_code.difference(machine_code))
        if not len(machine_code):
            didntcode_counter[machine_code_name].update(hand_code)
        if len(machine_code):
            didcode_counter[machine_code_name].update(hand_code)
            shot_and_missed[machine_code_name].update(hand_code.difference(machine_code))

        total_counter[machine_code_name].update(hand_code)


workbook = xlwt.Workbook()

for machine_code_name in counters:

    sheet = workbook.add_sheet(machine_code_name)
    sheet.write(0, 0, "Attribute Name")
    sheet.write(0, 1, "Count")
    for index, (name, count) in enumerate(counters[machine_code_name].items()):
        sheet.write(index+1, 0, name)
        sheet.write(index+1, 1, count)

    sheet = workbook.add_sheet("%s_individual" % machine_code_name)
    sheet.write(0, 0, "OCC")
    sheet.write(0, 1, "missed")
    sheet.write(0, 2, "total")
    sheet.write(0, 3, "didnt code")
    sheet.write(0, 4, "did code")
    sheet.write(0, 5, "precision")
    sheet.write(0, 6, "recall")
    for index, name in enumerate(sorted(missed_counter[machine_code_name].keys())):
        sheet.write(index+1, 0, name)

        miss = missed_counter[machine_code_name][name]
        sheet.write(index + 1, 1, miss)

        total = total_counter[machine_code_name][name]
        sheet.write(index + 1, 2, total)

        didnt = didntcode_counter[machine_code_name][name]
        sheet.write(index + 1, 3, didnt)

        did = didcode_counter[machine_code_name][name]
        sheet.write(index + 1, 4, did)

        if did != 0:
            precision = 1 - shot_and_missed[machine_code_name][name] / did
            sheet.write(index + 1, 5, precision)

        if total != 0:
            recall = 1 - miss / total
            sheet.write(index + 1, 6, recall)

workbook.save('output.xls')

pprint(dict(counters))
for k in sorted(list(total_counter.keys())):
    print( "%s: missed %s / %s" % (k, missed_counter[k], total_counter[k]))
