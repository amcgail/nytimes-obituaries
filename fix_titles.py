import occ
from os import path
from csv import DictReader, DictWriter
import csv

csv.field_size_limit(500 * 1024 * 1024)
inFn = path.join( path.dirname(__file__), "data","extracted.all.nice.csv" )
with open(inFn) as inF:
    dr = DictReader(inF)
    save_fieldnames = dr.fieldnames
    allEntries = list(dr)

for i, e in enumerate(allEntries):
    doc = occ.Doc(e)
    if i % 100 == 0:
        print( "%s / %s" % (i, len(allEntries) ) )
    e['name'] = str(doc.nameS)

with open(inFn+".csv", 'w') as outF:
    dw = DictWriter(outF, fieldnames=save_fieldnames)
    dw.writeheader()
    dw.writerows(allEntries)