# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 09:44:44 2017

@author: alec
"""
from itertools import chain
### LDA:

def ldaPrintResults(CV, model, n_words_to_print):
    print("Results:")
    topic_word = model.topic_word_
    vocab = CV.get_feature_names()
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_words_to_print:-1]
        print('Topic {}: {}'.format(i, ' '.join(topic_words)))

    cursesToLookFor = ["fuck", "shit", "ass", "asshole", "bullshit"]
    for w in cursesToLookFor:
        try:
            wi = vocab.index(w)
            print("%s in category %s" % (w, np.argmax(topic_word[:, wi])))
            print("Normalized category distribution of %s:" % w, (topic_word[:, wi] / np.max(topic_word[:, wi])))
        except ValueError:
            print("%s not found..." % w)

    print("\n\n")

def ldaAnalyzeDocs(docs, n_topics=10, n_words_to_print=10):
    import lda
    from sklearn.feature_extraction.text import CountVectorizer

    print("Initiating CountVectorizer...")
    CV = CountVectorizer(stop_words="english", min_df=0.01, max_df=0.40, token_pattern="[a-zA-Z]{4,}")
    print("Fitting CountVectorizer...")
    cv = CV.fit_transform(docs)

    print("Fitting LDA")
    model = lda.LDA(n_topics=n_topics, n_iter=1500, random_state=1)
    model.fit(cv)

    ldaPrintResults(CV, model, n_words_to_print)

    return model, CV

def getCountsDict(documents, max_ngram = 1):
    import numpy as np
    from sklearn.feature_extraction.text import CountVectorizer

    cv = CountVectorizer(decode_error='ignore', min_df=10, max_df=.5, ngram_range=(1, max_ngram),
                         binary=False,
                         max_features=15000)
    counts_mat = cv.fit_transform(documents).toarray()
    index_to_term = {v: k for k, v in cv.vocabulary_.iteritems()}
    return {index_to_term[i]: np.sum(counts_mat[i, :], axis=0) for i in range(counts_mat.shape[1])}

from FightingWords.fighting_words import basic_sanitize, bayes_compare_language

import occ
import nlp

# load the documents
N = 10000

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", N=N, rand=False)

group1 = [x for x in coder.obituaries if x['gender'] == "male"]
group2 = [x for x in coder.obituaries if x['gender'] == "female"]

def get_sentences(x):
    from random import sample
    x = nlp.sent_tokenize(x['fullBody'])
    return sample(x, min(10, len(x)))

group1 = chain.from_iterable( map( get_sentences, group1 ) )
group2 = chain.from_iterable( map( get_sentences, group2 ) )

group1 = list(group1)
group2 = list(group2)

l = min(len(group1), len(group2))
group1 = group1[:l]
group2 = group2[:l]

print(set(x['gender'] for x in coder.obituaries))

results = bayes_compare_language(group1, group2)

"""
results[:50]
Out[3]: 
[('her', -24.472638660062998, 28.0, 2824.0),
 ('ms', -15.231858740667622, 17.0, 709.0),
 ('mrs', -13.781184967615506, 11.0, 718.0),
 ('husband', -10.718720955655815, 10.0, 312.0),
 ('miss', -10.12306090145038, 7.0, 333.0),
 ('women', -9.800661396089723, 12.0, 219.0),
 ('sister', -8.166502208031874, 75.0, 223.0),
 ('woman', -7.896898742344207, 8.0, 141.0),
 ('mother', -7.7762146151254745, 32.0, 146.0),
 ('married', -6.9670811271333735, 39.0, 138.0),
 ('womens', -6.763406929428865, 4.0, 124.0),
 ('actress', -6.720139294578692, 6.0, 101.0),
 ('manhattan', -6.08938433911323, 248.0, 405.0),
 ('ballet', -5.638674596944467, 31.0, 99.0),
 ('daughter', -5.5919054106775015, 158.0, 276.0),
 ('nursing', -5.297987458422753, 10.0, 61.0),
 ('died', -5.062052382109721, 603.0, 792.0),
 ('social', -4.900423049170497, 30.0, 85.0),
 ('girl', -4.697095766748424, 3.0, 49.0),
 ('appeared', -4.554450072374274, 60.0, 123.0),
 ('child', -4.52756618756623, 15.0, 56.0),
 ('role', -4.372510629735085, 43.0, 96.0),
 ('lady', -4.370686745245447, 10.0, 46.0),
 ('broadway', -4.3135771296863625, 50.0, 105.0),
 ('york', -4.302341570796686, 409.0, 542.0),
 ('active', -4.273080950779724, 31.0, 77.0),
 ('widow', -4.233540144363422, 3.0, 38.0),
 ('debut', -4.18508489186525, 11.0, 45.0),
 ('center', -4.184445762994355, 105.0, 176.0),
 ('home', -4.152792786659142, 221.0, 318.0),
 ('young', -4.068862352008709, 55.0, 108.0),
 ('fashion', -4.068072372549198, 5.0, 35.0),
 ('hunter', -3.988761900516345, 6.0, 35.0),
 ('college', -3.9118792495931722, 166.0, 246.0),
 ('metropolitan', -3.8831925310477833, 16.0, 49.0),
 ('lawrence', -3.8821657231656377, 9.0, 38.0),
 ('volunteer', -3.850869009850325, 2.0, 33.0),
 ('singing', -3.844944971394035, 8.0, 36.0),
 ('teachers', -3.8003540422596513, 9.0, 37.0),
 ('opera', -3.7289877832905254, 30.0, 68.0),
 ('childrens', -3.691215470718652, 13.0, 42.0),
 ('new', -3.6852247946205, 603.0, 738.0),
 ('immediate', -3.678979651256813, 8.0, 34.0),
 ('life', -3.620009255259889, 78.0, 131.0),
 ('poetry', -3.5959796855487496, 6.0, 30.0),
 ('queen', -3.5458470374860203, 5.0, 28.0),
 ('henry', -3.542247868376204, 9.0, 34.0),
 ('at', -3.434417432647395, 1284.0, 1463.0),
 ('love', -3.3596956189371685, 27.0, 59.0),
 ('couple', -3.358527884126129, 9.0, 32.0)]
results[-50:]
Out[4]: 
[('1953', 3.381352127730161, 43.0, 16.0),
 ('from', 3.38897413256033, 876.0, 742.0),
 ('republican', 3.394100590897412, 37.0, 12.0),
 ('fellow', 3.427458771728139, 28.0, 6.0),
 ('officer', 3.4333722892721914, 71.0, 35.0),
 ('defense', 3.4668841773252153, 27.0, 5.0),
 ('formed', 3.5108356146911417, 32.0, 8.0),
 ('father', 3.5275231267047076, 90.0, 48.0),
 ('colonel', 3.6137917944580042, 27.0, 3.0),
 ('oil', 3.6334341097630523, 29.0, 5.0),
 ('princeton', 3.6378680910295698, 52.0, 20.0),
 ('games', 3.7174289780206067, 29.0, 4.0),
 ('business', 3.725623535680319, 101.0, 54.0),
 ('jr', 3.747662202226299, 85.0, 42.0),
 ('yale', 3.7845813037816174, 43.0, 13.0),
 ('harvard', 3.8044108676879023, 63.0, 26.0),
 ('game', 3.8909997709767, 35.0, 7.0),
 ('chief', 3.901044530009935, 101.0, 52.0),
 ('law', 3.9196458267031202, 128.0, 72.0),
 ('communist', 3.9209617769487175, 34.0, 6.0),
 ('force', 3.9318876725968517, 37.0, 8.0),
 ('labor', 3.9318876725968517, 37.0, 8.0),
 ('bank', 3.96480261203592, 53.0, 18.0),
 ('china', 3.989432134254588, 33.0, 4.0),
 ('manager', 4.081289427017348, 77.0, 33.0),
 ('professor', 4.132431601646986, 125.0, 67.0),
 ('firm', 4.216954450808093, 64.0, 23.0),
 ('president', 4.230008304316059, 306.0, 210.0),
 ('had', 4.2799604280142525, 615.0, 475.0),
 ('man', 4.319763272645449, 76.0, 30.0),
 ('space', 4.400906139131007, 41.0, 6.0),
 ('pacific', 4.5476797132215925, 43.0, 4.0),
 ('party', 4.6245615792620445, 79.0, 29.0),
 ('corporation', 4.70601277955644, 71.0, 23.0),
 ('air', 4.815351644429543, 54.0, 11.0),
 ('that', 4.8194251728434905, 830.0, 647.0),
 ('chairman', 4.954638807432094, 141.0, 68.0),
 ('military', 5.006448741056516, 52.0, 5.0),
 ('served', 5.040106482587069, 193.0, 105.0),
 ('war', 5.062185027688142, 238.0, 139.0),
 ('general', 5.348893409811934, 109.0, 41.0),
 ('army', 5.418659343349159, 73.0, 17.0),
 ('company', 6.159599668918411, 248.0, 127.0),
 ('retired', 6.169022710609245, 165.0, 68.0),
 ('former', 7.020345393756456, 296.0, 146.0),
 ('son', 7.055220765551404, 290.0, 141.0),
 ('him', 10.728850177382686, 258.0, 15.0),
 ('wife', 13.483410123070085, 392.0, 64.0),
 ('mr', 30.124184758698917, 1855.0, 173.0),
 ('his', 33.08071489168665, 2428.0, 137.0)]
"""