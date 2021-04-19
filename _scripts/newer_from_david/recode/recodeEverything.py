import sys
sys.path.append("/home/ec2-user/nytimes-obituaries/lib")
import occ

if False:
    occ.regenerateW2C()

coding_in = "v2.1"

if False:
    occ.codeAll(loadDirName=coding_in, toRecode=[
        "spacy_ents",
        "spacy_ents_PERSON",
        "spacy_ents_GPE",
        "spacy_ents_NORP",
        "spacy_ents_ORG",
        "whatTheyWere",
        "whatTheyDid"
    ], debug=False)


# just deletes a code
if False:
    print("DELETING CODES>.....")
    for obit in occ.obitIterator("v2.1"):
        del obit['OCC_syntax']
        obit.save("v2.1")

if False:
    print("CODING>......")
    occ.codeAll(loadDirName=coding_in, toRecode=[
        "OCC_syntax", "OCC_fullBody", "OCC_FsT_nobreaks"
    ], debug=False, onlyAbsent=True)

occ.codeAll(loadDirName=coding_in, toRecode=[
    "fs_corrupted",
    "title_corrupted",
    "not_obit",
    "name_prior",
    "best_name"
], debug=False, onlyAbsent=True, N=30)