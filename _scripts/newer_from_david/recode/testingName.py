import occ
from collections import Counter
import json

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", N=5, rand=False)

counts = Counter()

for i, obit in enumerate(coder.obituaries):
    if i % 100 == 0:
        print(i)

    print("(%s)" % obit['id'], "Previous name", obit['name'])
    #del obit['name_parts']
    #del obit['name']
    #print( "New parts", obit['name_parts'] )
    #print( "New name", obit['name'] )

    print(json.dumps( obit['name_prior'], indent=4) )
    print(obit['best_name'])
    print(obit['firstSentence'])
    print("---------")