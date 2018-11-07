import nlp, occ

n = 50

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.0", N=n*5, rand=False)

from collections import Counter
from itertools import chain
from collections import defaultdict

supergroups = {
    "s043": [2] + list(range(4,44)),
    "s050": range(50,74),
    "s080": range(80,96),
    "s100": range(100,125),
    "s130": range(131, 154),
    "s160": range(160, 197),
    "s200": range(200, 207),
    "s210": range(210, 216),
    "s220": range(220, 235),
    "s260": range(260, 297),
    "s300": range(300, 355),
    "s360": range(360, 366),
    "s370": range(370, 396),
    "s400": range(400, 417),
    "s420": range(420, 426),
    "s430": range(430, 466),
    "s470": range(470, 497),
    "s500": range(500, 594),
    "s600": range(600, 614),
    "s620": range(620, 677),
    "s680": range(680, 695),
    "s700": range(700, 763),
    "s770": range(770, 897),
    "s900": range(900, 976),
    "s980": range(980, 984),
    "s992": [992]
}

def canonicalize(x):
    if type(x) == str:
        try:
            x = int(x)
        except ValueError:
            return x.strip()

    if type(x) in [int, float]:
        x = "%03d" % int(x)
        return x

def get_supergroup(x):
    if not len(x):
        return x

    if x[0] == "s":
        return x

    try:
        z = int(x)
        for k in supergroups:
            if z in supergroups[k]:
                return k
    except ValueError:
        pass

    return "s^%s" % x
    raise Exception("%s not found" % x)


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
num_added = 0
for obit in coder.obituaries:
    if num_added >= n:
        break

    words = [x for x in nlp.word_tokenize(obit['firstSentence']) if x.lower() == x]
    hyps = list(chain.from_iterable( all_hypernyms(word) for word in words ))
    hypernyms.update(hyps)

    count = Counter(hyps)
    total_count += count

    occs = set(get_supergroup(canonicalize(x)) for x in chain.from_iterable(x['occ'] for x in obit['OCC']))
    if len(occs) != 1:
        continue

    all_occs.update(occs)

    training_set.append({
        "hyps": hyps,
        "occ": occs
    })

    num_added += 1

print( len(training_set), "examples loaded" )

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

    if np.sum(ind) != 0:
        ind = ind / np.sum(ind)

    return ind

#loss = tf.reduce_sum( tf.abs( tf.subtract( output, target ) ) )
#loss = tf.losses.sigmoid_cross_entropy(multi_class_labels=target, logits=output)
loss = -tf.reduce_sum( target * tf.log( tf.clip_by_value(output, 1e-10, 1) ) )
trainer = tf.train.GradientDescentOptimizer(1e-1).minimize( loss )

# Graph definition done , compile i t and feed concrete data .
# Only one data - point i s shown , in practice we w i l l use
# a data - feeding loop .
with tf.Session(config=tf.ConfigProto(log_device_placement=True)) as sess:
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
        print( loss_value )

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