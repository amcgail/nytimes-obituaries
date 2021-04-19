from operator import itemgetter
from random import randrange

import numpy as np
from scipy.sparse.csr import csr_matrix

from scipy.spatial.distance import cosine
from gensim.models import LsiModel

from sklearn.feature_extraction.text import TfidfVectorizer
from occ import OBIT_DB

nNeighborsToTrust = 10

original_docs = list( map(itemgetter("fullBody"), OBIT_DB.find().limit(1000)) )
vec = TfidfVectorizer(
    lowercase=True,
    ngram_range=(2,5),
    max_df=0.1,
    min_df=0.01
)

response = vec.fit_transform( original_docs )

assert(isinstance(response, csr_matrix))

# find the closest ones

vocab_list = vec.get_feature_names()

corpus = []
for doc in original_docs:
    my_transform = vec.transform([doc])
    indices = np.argwhere(my_transform)
    corpus.append( [ (i[1], my_transform[i[0],i[1]]) for i in indices ] )

model = LsiModel(corpus, id2word={i:x for i,x in enumerate(vocab_list)})

vectorized_corpus = model[corpus]

np_vectors = np.array([
    np.array([ x[1] for x in y ])
    for y in vectorized_corpus
    if y # for some reason it returns empty vectors!?
])

pick = randrange(start=0, stop=np_vectors.shape[0])

distances = [
    np.linalg.norm(
        np_vectors[pick] - np_vectors[i]
    )
    for i in range(np_vectors.shape[0])
]

def print_words(indexes):
    print(list(map(
        lambda x: vocab_list[x],
        list(indexes)
    )))

def print_top_keys(ni):
    print_words(np.argsort(-response[ni, :].toarray().flatten())[:10])

def print_nonzero(doci):
    print_words(np.argwhere(doc_counts[doci, :].toarray().flatten() != 0).flatten())

for d in original_docs:
    print(d)
    print(np.argwhere(vec.transform([d])))

nearest = np.argsort(distances)
nearest = nearest[1:nNeighborsToTrust]  # excluding the first

for ni in nearest:
    print_top_keys(ni)