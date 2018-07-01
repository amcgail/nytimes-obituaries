import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll")
# coder.codeAll(["OCC"])

for obit in coder.obituaries:
    for occ in obit["OCC"]:
        occ['occ'] = [ x['code'] for x in occ['occ'] ]

coder.dumpCodes("codingAll")