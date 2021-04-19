import occ

from operator import itemgetter
from itertools import groupby

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.0_extract", rand=False)

if False:
    for _, v in groupby(sorted(coder.obituaries, key=itemgetter("fullBody")), itemgetter("fullBody")):
        v = list(v)
        if len(v) <= 1:
            continue

        print({x['id'] for x in v})

        for doc in v[1:]:
            print("destroying '%s'" % doc['id'])
            doc.destroy_in_memory()

# ANOTHER WAY :(
todelete = []
for i,doc in enumerate(coder.obituaries):
    if i % 1000 == 0:
        print("Finished ",i," obituaries!")

    fb = doc['fullBody']
    fbchunk = fb[15:115]

    if len(fbchunk) <= 20:
        print("Too short: %s" % doc['id'])

    matches = [ d for d in coder.obituaries if d not in todelete and fbchunk in d['fullBody'] ]

    if len(matches) > 1:
        print("Duplicate found!")
        for d in matches[1:]:
            todelete.append(d)
            print("---" + d['title'])

for x in todelete:
    assert(isinstance(x, occ.Obituary))
    x.destroy_in_memory()