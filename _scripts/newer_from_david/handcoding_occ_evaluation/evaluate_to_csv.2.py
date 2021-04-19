from _csv import writer
from os.path import join, dirname

import xlrd
import xlwt

import occ
from xlutils.copy import copy
from collections import defaultdict
from itertools import chain, product
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

linux_home = "/home/alec/amcgail2@gmail.com/projects/nytimes-obituaries"
windows_home = "/Users/Alec McGail/amcgail2@gmail.com/projects/nytimes-obituaries"
infn = join(
    linux_home,
    "hand_coding_originals/hand coding ds as combined sample aug 24.xlsx.xlsx.xlsx"
)

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
total_occ_true = defaultdict(lambda: Counter())
total_occ_machine = defaultdict(lambda: Counter())
total_obits_by_algo = Counter()
falseNeg = defaultdict(lambda: Counter())
falsePos = defaultdict(lambda: Counter())
truePos = defaultdict(lambda: Counter())
someCode = defaultdict(lambda: Counter())

crossTab = defaultdict(lambda: Counter())

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

    occs = ['OCC',
            'OCC_FsT_nobreaks',
            'OCC_fullBody',
            'OCC_syntax',
            'OCC_title',
            'OCC_wikidata',
            'OCC_titleSyntaxU',
            'OCC_titleSyntaxI'
            ]

    all_machine_code = occ.obitFromId("v2.1", id)
    #OBIT_DB.find_one({"id": id})

    for machine_code_name in occs:

        machine_code = all_machine_code[machine_code_name]

        # process the machine code to a standard format
        print(machine_code)
        if machine_code == None:
            machine_code = set()
        elif type(machine_code) == list:
            if len(machine_code) and type(machine_code[0]) == dict:
                if 'occ' in machine_code[0]:
                    machine_code = list(chain.from_iterable(x['occ'] for x in machine_code))
                elif 'code' in machine_code[0]:
                    machine_code = [ x['code'] for x in machine_code ]
                else:
                    raise Exception("WTF is this?", machine_code)
            # what!?!?          this exists!?!?
            elif len(machine_code) and type(machine_code[0]) == list:
                machine_code = list( chain.from_iterable( chain.from_iterable(x['occ'] for x in y) for y in machine_code) )

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

        if len(machine_code):
            someCode[machine_code_name].update(hand_code)
            falseNeg[machine_code_name].update(hand_code.difference(machine_code))
            falsePos[machine_code_name].update(machine_code.difference(hand_code))
            truePos[machine_code_name].update(machine_code.intersection(hand_code))
            #trueNeg[machine_code_name].update(allCodes.minus(hand_code).minus())

            total_obits_by_algo.update({machine_code_name})

        total_occ_true[machine_code_name].update(hand_code)
        total_occ_machine[machine_code_name].update(machine_code)

        crossTab[machine_code_name].update( product( hand_code, machine_code ) )


for machine_code_name in counters:
    with open( join( dirname(__file__), "coded.actual.cross.%s.csv" % machine_code_name ), 'w' ) as csvf:
        csvw = writer(csvf)
        csvw.writerow([ "actual_OCC", "coded_OCC", "count" ])

        for (actual,coded), count in crossTab[machine_code_name].items():
            csvw.writerow([
                actual, coded, count
            ])

with open( join( dirname(__file__), "handcoding_eval.csv" ), 'w' ) as csvf:
    csvw = writer(csvf)
    csvw.writerow([
        "Algorithm", "OCC code",
        "Total true codes", "Total machine codes",
        "truePos", "falsePos", "falseNeg", "Guessed",
        "Precision", "Recall",
        "Pop Prop Guess", "Pop Prop True",
        "NobitsCoded"
    ])

    for machine_code_name in counters:

        for index, name in enumerate(sorted(total_occ_true[machine_code_name].keys())):
            total_true_code = total_occ_true[machine_code_name][name]
            total_machine_code = total_occ_machine[machine_code_name][name]

            #if total_machine_code == 0:
            #    continue

            falsen = falseNeg[machine_code_name][name]
            falsep = falsePos[machine_code_name][name]
            truep = truePos[machine_code_name][name]
            guessed = someCode[machine_code_name][name]

            algo_total_coded = total_obits_by_algo[machine_code_name]

            precision, recall = -1, -1
            if truep + falsep != 0:
                precision = truep / (truep + falsep)
            if truep + falsen != 0:
                recall = truep / (truep + falsen)

            csvw.writerow([
                machine_code_name, name,
                total_true_code, total_machine_code,
                truep, falsep, falsen, guessed,
                precision, recall,
                total_machine_code / algo_total_coded,
                total_true_code / 1000,
                algo_total_coded
            ])

occ.server.close()