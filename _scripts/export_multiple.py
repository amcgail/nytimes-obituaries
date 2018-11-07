from os import path
import nlp
import occ
import csv
import os
from random import sample
from itertools import chain
#from datetime.datetime import

outfn = "all.csv"
outputdir = path.join(path.dirname(__file__), "..", "exports")
noutput = 200

args_to_output = {
    "id":lambda x: x['id'],
    "date":lambda x: str(x['date']),
    "title":lambda x: x['title'],
    "OCC":lambda x: "|".join( set(chain.from_iterable( y['occ'] for y in x['OCC'])) ),
    "gender": lambda x: x['gender'].strip(),
    "firstSentence":lambda x: x['firstSentence'].strip(),
    "fullBody":lambda x: x['fullBody'].strip(),
    "wordCount":lambda x: len(x['fullBody'].split()),
    "sentenceCount":lambda x: len(nlp.sent_tokenize(x['fullBody'])),
    "age":lambda x: x['age']
}

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", rand=True)

# no filter whatsoever!
if True:
    obits_to_export = coder.obituaries#[:1000]

# filters by OCC --
if False:

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