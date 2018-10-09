from itertools import chain
import occ

coding = "codingAll"

coder = occ.Coder()
coder.loadPreviouslyCoded(coding)

#print( [x['firstSentence'] for x in coder.obituaries if "Tillich" in x['firstSentence']])

for x in coder.obituaries:
    print( list(chain.from_iterable(y['occ'] for y in x['OCC'])) )

teachers = [ x for x in coder.obituaries if "220" in list(chain.from_iterable( y['occ'] for y in x['OCC'] )) ]

print("\n\n-------------------\n\n".join( x['fullBody'] for x in teachers[:15] ))