import occ, nlp

coder = occ.Coder()
coder.loadDocs(N=1000, rand=False)
coder.codeAll(["OCC_new"])

for obit in coder.obituaries:
    try:
        t = obit['OCC_new'][0]['occ'][0]['term']
    except IndexError:
        continue

    if nlp.lemmatize( t ) == t:
        continue

    print(obit["title"])
    print(obit["firstSentence"])
    print(obit['OCC_new'])
    print()
