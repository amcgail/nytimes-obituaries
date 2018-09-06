import occ

if False:
    occ.regenerateW2C()

coding_in = "v2.0_extract"
#coding = "codingAll"
#coding_out = coding_in
coding_out = "v2.0"

coder = occ.Coder()
coder.loadPreviouslyCoded(coding_in, rand=False)
coder.codeAll(['OCC'])

coder.dumpCodes(coding_out)
