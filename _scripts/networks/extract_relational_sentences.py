import nlp
import occ

coding = "codingAll"

#coder = occ.Coder()
#coder.loadPreviouslyCoded(coding, N=500, rand=False)


s = nlp.spacy_parse("Mr. Sears, whose style combined many contrasts and inflections that alternated with enthusiastic staccato passages, played with Elmer Snowden, Andy Kirk, Lionel Hampton, Duke Ellington and Johnny Hodges.")
print( s[19], s[20] )
conjunctions = nlp.followRecursive(s[20], ["compound","conj"])

def isName(x):
    blacklist = ["universit", "college", "mr.", "ms.", "mrs.", "city", "center", "medical", "the", "county"]
    l = x.lower()
    for b in blacklist:
        if b in l:
            return False

    if len(x.split()) < 2:
        return False
    if any( y[0] == y[0].lower() for y in x.split() ):
        return False
    return True

relations = []

for doc in coder.obituaries:
    p = nlp.spacy_parse(doc['fullBody'])

    this_obit = []

    for s in list(p.noun_chunks)[1:]:
        if not isName(s.text):
            continue
        #print(s.start, s.end)
        #print( p[s.start], p[s.end] )
        if not str(p[s.start-1]) == "with":
            continue

        nlp.followRecursive()
        print(str(s.sent).replace(s.text, "**%s**"%s.text))

    relations += this_obit