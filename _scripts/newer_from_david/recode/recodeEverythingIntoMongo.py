import occ

coding_in = "v2.1"


if True:
    # transition to Mongo
    coder = occ.Coder()
    coder.loadPreviouslyCoded(coding_in, rand=False, N=1000, attrs=["age","id"])


if False:
    coder = occ.Coder()

    # just load everything!
    attributes = occ.attributeDb.find()
    coder.loadFromMongoAttributes(attributes)

    print(coder.obituaries[0].keys())

    # recode it
    coder.codeAttrsIntoMongo(["age"])