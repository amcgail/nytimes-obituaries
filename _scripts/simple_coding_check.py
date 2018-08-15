import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll", N=50, rand=False)

for x in coder.obituaries:
    print(x['firstSentence'])
    print(["[%s] %s: %s" % (y, code, occ.codeToName[code]) for y in x['OCC'] for code in y['occ']])
