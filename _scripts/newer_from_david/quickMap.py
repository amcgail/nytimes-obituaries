#52.112507	-8.95761	cross5	red	1	This is a fairly large cross on the map.
import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", N=2000)

nones = 0

for x in coder.obituaries:
    if x['location_died'] is not None:
        print("%s\t%s\tcross5\tred\t1\tTEST_TEXT" % (x['location_died']['lat'], x['location_died']['lon']))
    else:
        nones += 1

print(nones)