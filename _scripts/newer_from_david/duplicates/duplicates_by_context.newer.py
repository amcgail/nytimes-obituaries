from itertools import groupby

import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", rand=False, attrs=["name", "date_of_death", "title"])

obits = coder.obituaries
obits = list(filter(lambda x: x['name'] is not None, obits))

nondups = 0
dups = 0
for key, group in groupby(obits, lambda x: (x['date_of_death'], x['human_name'].last.upper())):
    group = list(group)
    if len(group) == 1:
        nondups += 1
        continue

    dups += 1
    print( [x['name'] for x in group] )

print(dups, nondups)