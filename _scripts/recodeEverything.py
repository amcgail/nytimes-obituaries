import occ

if False:
    occ.regenerateW2C()

coding = "all_v2.0"

coder = occ.Coder()
coder.loadPreviouslyCoded(coding, rand=False)
coder.codeAll(['OCC'])

if False:
    for obit in coder.obituaries:
        for occ in obit["OCC"]:
            occ['occ'] = [ x['code'] for x in occ['occ'] ]

coder.dumpCodes(coding)
