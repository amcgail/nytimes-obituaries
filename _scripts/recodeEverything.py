import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll")
coder.codeAll(["OCC"])
coder.dumpCodes("codingAll")