import csv
import json
from collections import defaultdict
from operator import attrgetter

import xlrd
from os import path

orig_handcoding_fn = path.join( path.dirname(__file__), "../../hand_coding_originals/hand coding ds as combined sample aug 24.xlsx.xlsx.xlsx")
workbook = xlrd.open_workbook(orig_handcoding_fn)

wksht = workbook.sheet_by_index(0)


all_rows = list(wksht.get_rows())
head, myrows = all_rows[0], all_rows[1:]

head = list(map(attrgetter("value"), head))
myrows = [
    list(map(attrgetter("value"), x))
    for x in myrows
]

myrows = [
    {
        head[i]: row[i]
        for i in range(len(row))
    }
    for row in myrows
]

print(json.dumps(myrows[0], indent=4))

output_headings = "id1	id2	name	occ group	job	citizen\tind	born	lived	died	education	title	comments\tfirstSentence	fullBody"
output_headings = output_headings.split("\t")

NUM_PEOPLE = 4
NUM_PER_PERSON = 100
OVERLAP_EACH_SIDE = 0
START = 91
outdir = path.join(path.dirname(__file__), "../../hand_coding_originals/automatic_slices")

assert(NUM_PEOPLE>1)
assert(NUM_PER_PERSON % 2 == 0)

for person_i in range(NUM_PEOPLE):
    if person_i == NUM_PEOPLE -1:
        # the end of the dataset
        my_start_1 = START + person_i * (NUM_PER_PERSON - OVERLAP_EACH_SIDE)
        my_end_1 = my_start_1 + (NUM_PER_PERSON - OVERLAP_EACH_SIDE) - 1

        my_start_2 = START
        my_end_2 = my_start_2 + OVERLAP_EACH_SIDE - 1

        sliced_rows = myrows[my_start_1-1:my_end_1] + myrows[my_start_2-1:my_end_2]

        date_str = "May 13 2019"
        outfn = path.join(outdir, "handcoding - {date_str} - slice {person_i} - {my_start_1}:{my_end_1} + {my_start_2}:{my_end_2}.csv".format(**locals()))
    else:
        my_start = START + person_i * (NUM_PER_PERSON - OVERLAP_EACH_SIDE)
        my_end = my_start + NUM_PER_PERSON - 1
        sliced_rows = myrows[my_start-1:my_end]

        date_str = "May 13 2019"
        outfn = path.join(outdir, "handcoding - {date_str} - slice {person_i} - {my_start} to {my_end}.csv".format(**locals()))

    output = []

    output.append(output_headings)

    for r in sliced_rows:
        myvals = defaultdict(lambda:'', {
            key: r[key]
            for key in ['title','firstSentence','fullBody','id1','id2']
        })

        myvals['id1'] = int(myvals['id1'])
        myvals['id2'] = int(myvals['id2'])

        output.append([
            myvals[x]
            for x in output_headings
        ])

    print("Writing to %s" % outfn)

    with open(outfn, 'w') as csvf:
        csvw = csv.writer(csvf)
        csvw.writerows( output )