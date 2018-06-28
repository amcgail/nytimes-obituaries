import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll")
coder.codeAll(["guess"])
coder.dumpCodes("codingAll")