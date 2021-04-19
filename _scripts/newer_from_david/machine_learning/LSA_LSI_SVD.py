# --------------------- IMPORTS --------------------------

from collections import defaultdict, Counter
from itertools import chain
from operator import itemgetter

from random import randrange

import numpy as np

from sklearn.cluster import DBSCAN

from gensim.corpora import Dictionary
from gensim.test.utils import common_dictionary, common_corpus, common_texts
from gensim.models import LsiModel

# just trying this on sentences from the OCCs
# -- maybe TDIDF transformed --
from gensim.utils import simple_preprocess

import nlp
import occ

# --------------------- PARAMS --------------------------

attemptToCluster = False
ndocs = 5000
# put more attention on the beginning of the obit
focusBeginning = False
# how much less each subsequent word counts
degeneration = 0.9999
nNeighborsToTrust = 50

# --------------------- THE REAL STUFF --------------------------

print("Loading docs.")
coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", N=ndocs, rand=False)
docs = coder.obituaries
text_docs = [ x['fullBody'] for x in docs ]

allOCCcounter = Counter(
    chain.from_iterable( occ.nice_occ(x['OCC']) for x in docs )
)

#text_docs = list(chain.from_iterable(
#    nlp.sent_tokenize(doc)
#    for doc in text_docs
#))

vector_docs = [
    simple_preprocess(doc)
    for doc in text_docs
]

dictionary = Dictionary(vector_docs)
dictionary.filter_extremes(no_below=5)
dictionary.filter_n_most_frequent(100)

# an example of giving more attention to the beginning of the document:
if focusBeginning == True:
    def generate_bag(doc):
        bag = defaultdict(int)

        ids = dictionary.doc2idx(doc)
        weight = 1
        for id in ids:
            # unknown words
            if id < 0:
                continue

            bag[id] += weight
            weight *= degeneration

        return sorted(list(bag.items()))
else:
    generate_bag = dictionary.doc2bow

vector_docs = [
    generate_bag(doc)
    for doc in vector_docs
]

# the documents have to be at least a few words long!
# otherwise everything goes to shit lol
vector_docs = list(filter(lambda x: len(x)>3, vector_docs))

model = LsiModel(vector_docs, id2word=dictionary)
vectorized_corpus = model[vector_docs]

# now try to cluster the vectors, and get some "types" of sentences, in some sense

np_vectors = np.array([
    np.array([ x[1] for x in y ])
    for y in vectorized_corpus
    if y # for some reason it returns empty vectors!?
])

# test some random indices
# I should write these tests more often!
for i in range(5):
    to_test = randrange(start=0, stop=np_vectors.shape[0])
    assert np.all(
        np_vectors[to_test] == \
        np.array([ x[1] for x in model[vector_docs[to_test]] ])
    )

print("Finding some nearest neighbors")
for i in range(10):
    find_nearest = randrange(start=0, stop=np_vectors.shape[0])

    distances = [
        np.linalg.norm(
            np_vectors[find_nearest] - np_vectors[i]
        )
        for i in range(np_vectors.shape[0])
    ]
    nearest = np.argsort(distances)

    nearest = nearest[:5]
    for doc_i in nearest:
        print(" - OCC: %s, similarity: %s" % (occ.nice_occ(docs[doc_i]['OCC']), distances[doc_i]) )
        print(" -- %s..." % (text_docs[doc_i][:100]))

    for i in range(3):
        print("----------")

print("Nearest neighbors now vote")
numcoded = 0
# we only care about the 10 most common
occs_to_care_about = list(map(itemgetter(0), allOCCcounter.most_common(10)))

while numcoded < 10:
    find_nearest = randrange(start=0, stop=np_vectors.shape[0])

    distances = [
        np.linalg.norm(
            np_vectors[find_nearest] - np_vectors[i]
        )
        for i in range(np_vectors.shape[0])
    ]

    nearest = np.argsort(distances)
    nearest = nearest[1:nNeighborsToTrust] #excluding the first

    counter = Counter()
    counter_inverse = Counter()
    counter_distance = Counter()
    for doc_i in nearest:
        # this one really seems to suck...
        counter_inverse.update({
            occ_code: 1/allOCCcounter[occ_code]
            for occ_code in occ.nice_occ(docs[doc_i]['OCC'])
            # if allOCCcounter[occ_code] > 5 # we don't want 1-offs spoiling the results...
            if occ_code in occs_to_care_about
        })

        counter.update({
            occ_code: 1
            for occ_code in occ.nice_occ(docs[doc_i]['OCC'])
            if allOCCcounter[occ_code] > 5 # we don't want 1-offs spoiling the results...
            if occ_code in occs_to_care_about
        })

        counter_distance.update({
            occ_code: 1 / distances[doc_i]
            for occ_code in occ.nice_occ(docs[doc_i]['OCC'])
            if allOCCcounter[occ_code] > 5  # we don't want 1-offs spoiling the results...
            if occ_code in occs_to_care_about
        })

    # deciding whether there's agreement, or contention
    votes = {
        counter.most_common(1)[0][0],
        counter_distance.most_common(1)[0][0]
    }

    already_coded = occ.nice_occ(docs[find_nearest]['OCC'])

    if False:
        # run this if you want to skip codes which conflict, etc.
        if len(already_coded):
            continue

        # note that set() is a subset of any set.
        if not already_coded.issubset(votes):
            continue

        if not len(votes) == 1:
            continue

    print(text_docs[ find_nearest ][:100])
    print("coded: ", [ occ.codeToName[x] for x in occ.nice_occ(docs[ find_nearest ]['OCC']) ])
    print("nearest (simple count): ", [ (occ.codeToName[x[0]], x[1]) for x in counter.most_common(3) ])
    print("nearest (weight by distance): ", [(occ.codeToName[x[0]], x[1]) for x in counter_distance.most_common(3)])
    print("nearest (inverse law): ", [ (occ.codeToName[x[0]], x[1]) for x in counter_inverse.most_common(3) ])

    print( len(counter) )

    for i in range(3):
        print("----------")

    numcoded += 1

if attemptToCluster:
    print("Attempting to cluster...")

    clustering_model = DBSCAN()
    clustering_model.fit(np_vectors)

    all_labels = np.unique(clustering_model.labels_)
    print("Listing output of 10/%s clusters found with DBSCAN" % len(all_labels))

    for label in all_labels:
        print("10 docs from label %s:" % label)
        for doc_i in np.where(clustering_model.labels_ == label)[0][:10]:
            print(" -- %s..." % text_docs[doc_i][:100])