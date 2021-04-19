import nlp, occ

coder = occ.Coder()

if False:
    coder.loadDocs(N=5000, rand=False)
    coder.codeAll()
    coder.dumpCodes("smallTest")

coder.loadPreviouslyCoded("codingAll", N=25000, rand=False)

from collections import Counter
from itertools import chain
from collections import defaultdict


_all_hyponyms_cache = {}
def all_hyponyms_synset_lemma( synset ):
    if synset in _all_hyponyms_cache:
        return _all_hyponyms_cache[synset]

    all_hyp = set()
    prev_ss = [synset]
    while 1:
        if len(prev_ss) == 0:
            break

        new_hyp = set()
        for x in prev_ss:
            new_hyp.update( x.hyponyms() )

        all_hyp.update(new_hyp)
        prev_ss = new_hyp

    all_hyp = chain.from_iterable( map(lambda x: x._lemma_names, all_hyp) )
    all_hyp = map(lambda x: x.replace("_"," "), all_hyp)
    all_hyp = set(all_hyp)

    _all_hyponyms_cache[synset] = all_hyp
    return all_hyp


_all_hypernyms_cache = {}
def all_hypernyms( word ):
    lemma = nlp.lemmatize(word)
    if lemma in _all_hypernyms_cache:
        return _all_hypernyms_cache[lemma]

    all_hyp = set()
    prev_ss = nlp.wn.synsets(lemma)
    while 1:
        if len(prev_ss) == 0:
            break

        new_hyp = set()
        for x in prev_ss:
            new_hyp.update( x.hypernyms() )

        all_hyp.update(new_hyp)
        prev_ss = new_hyp

    _all_hypernyms_cache[lemma] = all_hyp
    return all_hyp

hyper_occ_counter = defaultdict(lambda: defaultdict(int))
word_occ_counter = defaultdict(lambda: defaultdict(int))

# just go through first sentences and tabulate words that correspond to occs
for obit in coder.obituaries:
    words = nlp.word_tokenize( obit["firstSentence"] )
    words = map(str.lower, words)
    words = set(map(nlp.lemmatize, words))

    occs = set( chain.from_iterable(x['occ'] for x in obit["OCC"]) )
    if len(occs) != 1:
        continue

    code = list(occs)[0]

    for word in words:
        word_occ_counter[word][code] += 1


# now expand each word into its hypernyms
for word in word_occ_counter:

    vals = sorted(word_occ_counter[word].values())

    #if len(vals) > 5:
    #    continue

    most = vals.pop()

    if most < 10:
        continue

    if len(vals) >= 2:
        nextmost = vals.pop()

        # if most popular is 5 times more popular than second most popular,
        if most < nextmost * 4:
            continue

    code = sorted(word_occ_counter[word].keys(), key=lambda k: word_occ_counter[word][k])[-1]

    hypers = all_hypernyms(word)
    for hyper in hypers:
        hyper_occ_counter[hyper][code] += 1

CSV = []
CSV.append(["OCC", "term", "synset"])

for hyper in hyper_occ_counter:

    occs = hyper_occ_counter[hyper]
    if len(occs) > 1:
        continue

    occ = list(occs.keys())[0]
    num = list(occs.values())[0]

    if num <= 1:
        continue

    for term in all_hyponyms_synset_lemma(hyper):
        CSV.append([ occ, term, hyper.name() ])

    print( hyper, hyper_occ_counter[hyper] )
    print( "yielding: " )
    print( ", ".join( all_hyponyms_synset_lemma(hyper) ) )
    print()









if False:

    # direct copy from Goldberg, Yoav (2017)
    import tensorflow as tf

    W1 = tf.get_variable("W1" , [20, 150])
    b1 = tf.get_variable("b1" , [ 20 ] )
    W2 = tf.get_variable("W2" , [17 , 20])
    b2 = tf.get_variable("b2" , [ 17 ] )
    lookup = tf.get_variable("W" , [100 , 50])

    def get_index(x):
        pass # Logic omitted

    p1 = tf.placeholder( tf.int32 , [ ] )
    p2 = tf.placeholder( tf.int32 , [ ] )
    p3 = tf.placeholder( tf.int32 , [ ] )

    target = tf.placeholder( tf.int32 , [ ] )

    v_w1 = tf.nn.embedding_lookup( lookup , p1)
    v_w2 = tf.nn.embedding_lookup( lookup , p2)
    v_w3 = tf.nn.embedding_lookup( lookup , p3)

    x = tf.concat( [v_w1, v_w2, v_w3] , 0)

    output = tf.nn.softmax(
        tf.einsum("ij ,j->i" , W2, tf.tanh(
            tf.einsum("ij ,j->i" , W1, x) + b1) ) + b2)

    loss = -tf.log( output[ target ] )
    trainer = tf.train.GradientDescentOptimizer(0.1).minimize( loss )

    # Graph definition done , compile i t and feed concrete data .
    # Only one data - point i s shown , in practice we w i l l use
    # a data - feeding loop .
    with tf.Session() as sess:
        sess.run( tf.global_variables_initializer() )
        feed_dict = {
            p1 : get_index("the") ,
            p2 : get_index("black") ,
            p3 : get_index("dog") ,
            target: 5
        }
        loss_value = sess.run( loss, feed_dict )

        # update , no c a l l o f backward n e c e s s a r y
        sess.run( trainer, feed_dict )