import occ
import nlp

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", N=50, rand=False)

for x in coder.obituaries:
    #del x['OCC']
    del x['spacyName']
    print(x['firstSentence'])
    print(x['spacyName'])
    print(x._OCC_just_appos())
    #print(["[%s] %s: %s" % (y, code, occ.codeToName[code]) for y in x._OCC_just_appos() for code in y['occ']])
