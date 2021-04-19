import occ
from collections import Counter

attr_to_clear = "spacyName"

wwiiCounter = Counter()

for i, obit in enumerate(occ.obitIterator("v2.1")):
    wwiiCounter.update( ["World War II" in obit['fullBody']] )
    if (i+1) % 1000 == 0:
        print(wwiiCounter)