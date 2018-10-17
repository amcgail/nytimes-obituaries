import occ
from itertools import chain
import nlp

# load the documents
N = 1000

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", N=N, rand=False)

html_parts = []

for obit in coder.obituaries:
    occ = obit['OCC']
    occs = set( chain.from_iterable( x['occ'] for x in occ ) )

    if "001" not in occs:
        continue

    myh = obit['fullBody']
    myh = "<p>%s</p>" % myh
    for x in businesses:

    print(obit['fullBody'])
    print("---------------")
    print("---------------")
    print("---------------")