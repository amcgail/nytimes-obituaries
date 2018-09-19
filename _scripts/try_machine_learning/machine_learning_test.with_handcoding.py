import nlp, occ

coder = occ.Coder()

if False:
    coder.loadDocs(N=5000, rand=False)
    coder.codeAll()
    coder.dumpCodes("smallTest")

coder.loadPreviouslyCoded("v2.0")

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


training_set = []

# start by collecting the hypernyms
hypernyms = set()
all_occs = set()

total_count = Counter()
for obit in coder.obituaries[:5000]:
    words = [x for x in nlp.word_tokenize(obit['firstSentence']) if x.lower() == x]
    hyps = list(chain.from_iterable( all_hypernyms(word) for word in words ))
    hypernyms.update(hyps)

    count = Counter(hyps)
    total_count += count

    occs = set(chain.from_iterable(x['occ'] for x in obit['OCC']))
    all_occs.update(occs)

    training_set.append({
        "hyps": hyps,
        "occ": occs
    })

hypernyms = list(hypernyms)
all_occs = sorted(list(all_occs))

# direct copy from Goldberg, Yoav (2017)
import tensorflow as tf
import numpy as np

n_wordnets = len(hypernyms)
n_occs = len(all_occs)

hidden_size = (n_wordnets + n_occs) // 2

W1 = tf.get_variable("W1" , [hidden_size, n_wordnets])
b1 = tf.get_variable("b1" , [ hidden_size ], tf.float32 )

W2 = tf.get_variable("W2" , [n_occs , hidden_size])
b2 = tf.get_variable("b2" , [ n_occs ], tf.float32 )

x = tf.placeholder( tf.float32, [ n_wordnets ] )

p1 = tf.einsum("ij,j->i" , W1, x) + b1
p2 = tf.einsum("ij,j->i" , W2, tf.tanh(p1)) + b2
output = tf.nn.softmax(p2)

target = tf.placeholder( tf.float32, [ n_occs ] )

def get_wordnet_vector(hyps):
    method = 1
    if False:
        # simple, 1-hot. there or not!
        wn = np.array( [ int(x in hyps) for x in hypernyms ] )
    else:
        # weighted by the count. more nuanced.
        h_count = Counter(hyps)
        wn = np.array([h_count[x] for x in hypernyms])
    return wn / np.sum(wn)

def get_occ_index( occs ):
    ind = np.array( [ int(x in occs) for x in all_occs ] )
    return ind / np.sum(ind)

#loss = tf.reduce_sum( tf.abs( tf.subtract( output, target ) ) )
#loss = tf.losses.sigmoid_cross_entropy(multi_class_labels=target, logits=output)
loss = -tf.reduce_sum( tf.multiply( target, tf.log( tf.clip_by_value(output, 1e-10, 1) ) ) )
trainer = tf.train.GradientDescentOptimizer(1e-1).minimize( loss )

# Graph definition done , compile i t and feed concrete data .
# Only one data - point i s shown , in practice we w i l l use
# a data - feeding loop .
with tf.Session() as sess:

    n = 100
    split = 0.8
    split_i = int(n*0.8)

    sess.run(tf.global_variables_initializer())

    for training_ex in training_set[:split_i]:
        if not np.sum( get_occ_index(training_ex['occ']) ):
            continue

        feed_dict = {
            x : get_wordnet_vector( training_ex['hyps'] ),
            target: get_occ_index( training_ex['occ'] )
        }
        loss_value = sess.run( loss, feed_dict )
        print( np.log( output.eval({
            x : get_wordnet_vector( training_ex['hyps'] ),
            target: get_occ_index( training_ex['occ'] )
        }) ))

        # update, no need to call backward (it's included?)
        sess.run( trainer, feed_dict )

    for training_ex in training_set[split_i:]:
        print(
            "predicted: ",
            all_occs[ np.argmax( output.eval({
                x : get_wordnet_vector( training_ex['hyps'] ),
                target: get_occ_index( training_ex['occ'] )
            }) ) ],
            "'actual'",
            training_ex['occ']
        )