import occ

coder = occ.Coder()
coder.loadDocs(N=100, rand=False)
coder.codeAll(["guess"])

for obit in coder.obituaries:
    print(obit['guess'])