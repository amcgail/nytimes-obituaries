import occ

if False:
    # just tests if it works well on 10000 docs.

    coder = occ.Coder()
    coder.loadPreviouslyCoded("codingAll", N=10000, rand=False)

    kins = [x for x in coder.obituaries if len(x['kinship'])]
    print("\n".join( str(x['kinship']) + ": " + x['firstSentence'] for x in kins ))

if True:
    # code the mutha for everything

    coder = occ.Coder()
    coder.loadPreviouslyCoded("codingAll")

    coder.codeAll(["kinship"])

    coder.dumpCodes("codingAll")