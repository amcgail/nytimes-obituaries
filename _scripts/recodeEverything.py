import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll")
for x in coder.obituaries:
    del x["guess"]

coder.codeAll(["OCC"])
coder.dumpCodes("codingAll")