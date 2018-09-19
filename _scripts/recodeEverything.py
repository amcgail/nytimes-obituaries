import occ

if True:
    occ.regenerateW2C()

coding_in = "v2.1"
#coding = "codingAll"
#coding_out = coding_in
coding_out = "v2.1"

coder = occ.Coder()
coder.loadPreviouslyCoded(coding_in, rand=False)
coder.codeAll(['OCC'])

coder.dumpCodes(coding_out)
