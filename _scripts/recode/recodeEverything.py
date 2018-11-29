import occ

if False:
    occ.regenerateW2C()

coding_in = "v2.1"
#coding = "codingAll"
#coding_out = coding_in
coding_out = "v2.1"

occ.codeAll(loadDirName="v2.1", toRecode=["namesInObit"], debug=False)
#occ.codeAll(loadDirName="v2.1", toRecode=["namesInObit"], N=100, debug=True)

#print("\n".join( sorted(coder.obituaries[0].keys())) )

#print(coder.obituaries[0]._prop_cache)
#print("OCC" in coder.obituaries[0]._prop_cache)

#coder.dumpCodes(coding_out)