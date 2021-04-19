from operator import itemgetter
from collections import Counter, defaultdict
from random import sample

from nlp import word_tokenize

from wiki import isXsubclassY
import occ

scientist = "Q901"
artist = "Q483501"

expandToFullSentence = True

relevant_words = isXsubclassY("P279", scientist)
relevant_words = set(map(itemgetter("name"), relevant_words))

occupationCounter = Counter()
firstSentences = defaultdict(list)

for i, obit in enumerate(occ.obitIterator("v2.1")):
    inters = set(obit["appos_words"]).intersection(relevant_words)
    if len(inters):
        #print(inters)
        #print(obit['firstSentence'])

        if expandToFullSentence:
            inters.update(set(word_tokenize(obit['firstSentence'])).intersection(relevant_words))

        occupationCounter.update(inters)
        for occNoun in inters:
            firstSentences[occNoun].append(obit['firstSentence'])

    if i % 2000 == 0:
        print("\n\n\n")
        print("Iteration", i)
        for occNoun, count in occupationCounter.most_common(20):
            print("------ %s %s ------" % (occNoun, count))
            for s in sample(firstSentences[occNoun], min(len(firstSentences[occNoun]), 10)):
                print(s)
        print(occupationCounter.most_common(20))

print(occupationCounter)
#print(scientist_words[:10])
#print(len(scientist_words))