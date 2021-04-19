from csv import writer
from datetime import datetime
from os.path import dirname, join

import occ


def cleanItUp(inp):
    if type(inp) == datetime:
        return datetime.strftime(inp, "%Y-%m-%d")
    return inp

with open( join( dirname(__file__), "allObitsOCC.csv" ), 'w' ) as csvf:
    csvw = writer(csvf)

    for i, obit in enumerate(occ.obitIterator("v2.1")):
        if i % 1000 == 0:
            print("Processing document %s" % i)

        OCCkeys = [
            "OCC",
            #"OCC_syntax",
            #"OCC_title",
            #"OCC_wikidata",
        ]

        keys = [
            "date",
            "date_of_death",
            "name",
            "title",
            "gender"
        ]

        for occk in OCCkeys:
            occPart = [
                "|".join( list(set(obit[occk][i]['occ'])) ) if i < len(obit[occk]) else None
                for i in range(10)
            ]

            csvw.writerow([occk] + occPart + [
                cleanItUp(obit[k]) for k in keys
            ])