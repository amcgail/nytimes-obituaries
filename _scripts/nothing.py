toexport = [
    "
]

import nlp
from itertools import chain

def all_hyponyms_synset_lemma( synset ):
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
    return all_hyp

for name in toexport:
    hypos = all_hyponyms_synset_lemma(nlp.wn.synset(name))
    for hypo in hypos:
        print(",".join([name, hypo]))