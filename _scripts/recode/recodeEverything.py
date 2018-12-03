import sys
sys.path.append("/home/ec2-user/nytimes-obituaries/lib")
import occ

if False:
    occ.regenerateW2C()

coding_in = "v2.1"
occ.codeAll(loadDirName=coding_in, toRecode=[
    "spacy_ents",
    "spacy_ents_PERSON",
    "spacy_ents_GPE",
    "spacy_ents_NORP",
    "spacy_ents_ORG",
    "whatTheyWere",
    "whatTheyDid"
], debug=False)