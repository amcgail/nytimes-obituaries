import occ
from collections import Counter

coding_in = "v2.1"

coder = occ.Coder()
coder.loadPreviouslyCoded(coding_in, rand=False, N=500, attrs=["namesInObit", "id", "name"])

# unique_human_names = []

nameCounter = Counter()
for obit in coder.obituaries:
    nameCounter.update(obit['namesInObit'])


network = Counter()

# coreference network
for obit in coder.obituaries:
    names = set(obit['namesInObit'])
    names = list(filter(lambda x: nameCounter[x] > 1, names))
    network.update(
        (x,y) for x in names for y in names if x>y
    )

print(network.most_common(10))

# this is the easiest...
# could then try collapsing for the most common ones
# collapsing only works... hmmmmmmmmmmmmm

# ARGH IT TAKES TOO LONG
# How can this be possible?
# How can I disambiguate slightly different names?
# There's a systematic way, but I'm confused...

obit_names = set(x['name'] for x in coder.obituaries)
obit_names = [HumanName(x) for x in obit_names]

# definitely only first names...
obit_names = [x for x in obit_names if x.first]

def inObitNames(name):
    name = HumanName(name)
    for on in obit_names:
        if on.supercedes(name):
            return True

within_obits = Counter()
# reference network within obits
for obit in coder.obituaries:
    names = set(obit['namesInObit'])
    names = list(filter(inObitNames, names))

    within_obits.update(
        (obit['name'], x) for x in names
    )

print(within_obits.most_common(10))