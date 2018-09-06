from os import path
import occ
import csv
import os

outfn = "hand_coding_7_10more.csv"
noutput = 10

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll", N=noutput*2, rand=True)

hand_coding_dir = path.join( path.dirname(__file__), "..", "hand_coding_originals" )

old_ids = set()
for partial_fn in os.listdir(hand_coding_dir):
    fn = path.join(hand_coding_dir, partial_fn)
    with open(fn) as f:
        old_ids.update( int(x['id']) for x in csv.DictReader(f) )

csv_rows = [
    [
        obit['id'],
        obit['title'],
        obit['firstSentence'],
        obit['fullBody']
    ]
    for obit in coder.obituaries
    if int(obit['id']) not in old_ids
]
print(len(csv_rows))
csv_rows = csv_rows[:noutput]

with open(path.join(hand_coding_dir, outfn), 'w') as outf:
    csvw = csv.writer(outf)
    csvw.writerow(["id", "title", "firstSentence", "fullBody"])
    csvw.writerows(csv_rows)