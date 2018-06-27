# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 09:44:44 2017

@author: alec
"""

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