import sys
sys.path.append("/home/ec2-user/nytimes-obituaries/lib")
import occ

if False:
    occ.regenerateW2C()

coding_in = "v2.1"
occ.codeAll(loadDirName="v2.1", toRecode=["namesInObit"], debug=False)
