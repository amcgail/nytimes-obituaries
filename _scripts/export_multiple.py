from os import path
import occ
import csv
import os
from random import sample
from itertools import chain
from datetime.datetime import

outfn = "001.200.csv"
outputdir = path.join(path.dirname(__file__), "..", "exports")
noutput = 200

args_to_output = {
    "id":lambda x: x['id'],
    "date":lambda x: str(x['date']),
    "title":lambda x: x['title'],
    "firstSentence":lambda x: x['firstSentence'],
    "fullBody":lambda x: x['fullBody']
}

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1")

obits_filter_occ = list(filter( lambda x: "001" in chain.from_iterable(y['occ'] for y in x['OCC']), coder.obituaries ))

years = sorted(set(x['date'].year for x in obits_filter_occ))
nyears = len(years)

print(years)

if not os.path.exists(outputdir):
    os.mkdir(outputdir)

obits_to_export = []

for yr in years:
    nthisyear = noutput // nyears

    obits_this_year = list(filter(lambda x: x['date'].year == yr, obits_filter_occ))
    to_output = sample(obits_this_year, min( len(obits_this_year), nthisyear))
    obits_to_export += to_output

csv_rows = [
    [
        param( obit ) for param in args_to_output.values()
    ]
    for obit in obits_to_export
]
print(len(csv_rows))
#csv_rows = csv_rows[:noutput]

with open(path.join(outputdir, outfn), 'w') as outf:
    csvw = csv.writer(outf)
    csvw.writerow(args_to_output.keys())
    csvw.writerows(csv_rows)