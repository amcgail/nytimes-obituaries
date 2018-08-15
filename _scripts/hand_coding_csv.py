import occ
import csv

outfn = "hand_coding_4.csv"
noutput = 100

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll", N=noutput, rand=True)

csv_rows = [
    [
        obit['id'],
        obit['title'],
        obit['firstSentence'],
        obit['fullBody']
    ]
    for obit in coder.obituaries
]

with open(outfn, 'w') as outf:
    csvw = csv.writer(outf)
    csvw.writerow(["id", "title", "firstSentence", "fullBody"])
    csvw.writerows(csv_rows)