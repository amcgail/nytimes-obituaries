import csv

import occ
from nlp import HumanName
from collections import Counter

coding_in = "v2.1"

coder = occ.Coder()
coder.loadPreviouslyCoded(coding_in, rand=False, attrs=["namesInObit", "id", "name"])

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

obit_names = set(x['name'] for x in coder.obituaries)

within_obits = Counter()
# reference network within obits
for obit in coder.obituaries:
    if obit['name'] == '<name not found>':
        continue

    names = set(obit['namesInObit'])
    names = [x for x in names if x != obit['name'] and x in obit_names]

    within_obits.update(
        (obit['name'], x) for x in names
    )

for n_top in [100, 500, 1000]:
    with open("cocitation.top%d.csv" % n_top, "w") as csvf:
        csvw = csv.writer(csvf)
        csvw.writerow(["from","to","n"])
        for ft, n in network.most_common(n_top):
            csvw.writerow(list(ft)+[n])

with open("within_obits.csv", "w") as csvf:
    csvw = csv.writer(csvf)
    csvw.writerow(["from","to"])
    for f,t in set(within_obits):
        csvw.writerow([f,t])