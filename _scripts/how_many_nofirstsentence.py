from collections import Counter
import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll")

cfs = Counter([len(x["firstSentence"]) for x in coder.obituaries])

print(", ".join( str(cfs[x]) for x in range(20) ))
