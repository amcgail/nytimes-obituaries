from csv import writer
from datetime import datetime
from itertools import chain
from os.path import dirname, join

import occ

grouping = {
    "CEO": {1,"001a","1a"},
    "ADMIN": {2}.union( set(range(4,43)) ),
    "LEGISLATOR": {3},
    "DIPLOMAT": {43, "s043"},
    "BIZOP": set(range(50,74)),
    "FINANCE": set(range(80,96)),
    "MATH": set(range(100,125)),
    "ARCHITECT": {130,131,"s130"},
    "ENGINEER": set(range(132,157)),
    "SCIENTIST": set(range(160,197)).union({"s160"}),
    "COUNSELOR": set(range(200,203)),
    "CLERGY": {204,205,206},
    "LAWYER": {210, 214, 215},
    "JUDGE": {211},
    "PROF": {220, "s220"},
    "TEACHER": set(range(230,235)),
    "EDUC OTHER": set(range(240,256)),
    "ARTIST": {260},
    "ACTOR": {270},
    "DIRECTOR": {271},
    "ATHLETE": {272}, # also had 276??
    "DANCER": {274},
    "MUSICIAN": {275},
    "CLOWN": {276},
    "ANNOUNCER": {280},
    "NEWS": set(range(281,284)),
    "PHOTO": {291,292},
    "AUTHOR": {284,285},
    "ARTS OTHER": {263}.union(set(range(286,297))),
    "DOCTOR": set(range(300,307)).union({312, "s300"}),
    "NURSE": [311]+list(range(313,356))+list(range(360,366)),
    "COP": range(370,396),
    "SALES": range(470,497),
    "SECRETARY": range(500,594),
    "FARM": range(600,614),
    "BLUE COLLAR": range(620,976),
    "PERSONAL": range(400,466),
    "MILITARY": [980,981,982,"s980"],
}

with open("grouping_summary.csv","w") as outf:
    w = writer(outf)
    w.writerow(["group", "OCCs"])
    for key, vals in grouping.items():
        w.writerow( [key, ", ".join( map(str,vals) )] )

reverse_map = {}
for k,vg in grouping.items():
    for code in vg:
        reverse_map[code] = k

def canonicalize(x):
    if type(x) == str:
        x = x.strip()
        try:
            x = int(x)
        except ValueError:
            pass

    return reverse_map[x]

    raise Exception("Couldn't find %s" % x)



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
            #"gender"
        ]

        for occk in OCCkeys:
            occs = chain.from_iterable(  obit[occk][i]['occ'] for i in range(len(obit[occk])) )
            occs = list(set(map(canonicalize, occs)))
            occPart = [occs[i] if i < len(occs) else None for i in range(10)]
            # print(occPart)

            csvw.writerow([occk] + occPart + [
                cleanItUp(obit[k]) for k in keys
            ])