db_to_match = "v2.0_extract"
output_db = "v2.0_matchid"

step = -1

if step == -2:
    # just see how many I have left to match...

    import occ
    coder = occ.Coder()
    coder.loadPreviouslyCoded("codingAll")
    print( "%s / %s" % ( len([ x for x in coder.obituaries if x['id'] >= 1000000 ]), len(coder.obituaries)) )

if step == -1:
    # persist them forever, so we don't forget what the IDs are!!

    import csv
    import occ

    outfn = "id_map.csv"

    with open(outfn, 'w') as outf:
        csvw = csv.writer(outf)

        coder = occ.Coder()
        coder.loadPreviouslyCoded(db_to_match)

        for d in coder.obituaries:
            csvw.writerow([
                d['id'],
                d['originalFile'],
                d['_d_id']
            ])

if step==3:
    import datetime
    import occ, nlp

    coder_ref = occ.Coder()
    coder_ref.loadPreviouslyCoded("codingAll")

    for d in coder_ref.obituaries:
        d['date'] = datetime.datetime.strptime(d['_date'], "%B %d, %Y")

    coder = occ.Coder()
    coder.loadPreviouslyCoded(db_to_match)

    for d in coder.obituaries:
        if d['id'] < 1000000:
            continue

        # match by name and date
        search1 = [
            x for x in coder_ref.obituaries
            if (x['name'] in d['name'] or d['name'] in x['name'])  and x['date'] == d['date'] and min(len(x['name']), len(d['name']) > 8)
        ]
        #search2 = [
        #    x for x in coder_ref.obituaries
        #    if x['date'] == d['date'] and (
        #        (set(x['firstSentence']) in set(d['firstSentence']))
        #        or (set(d['firstSentence']) in set(x['firstSentence']))
        #    )
        #]

        if len(search1) == 1:
            r = search1[0]

            print(d['firstSentence'])
            print(r['firstSentence'])
            print("------------------")
            print(r['id'])

            d['id'] = r['id']

    coder.dumpCodes(db_to_match)


if step==2:
    import datetime
    import occ, nlp

    coder_ref = occ.Coder()
    coder_ref.loadPreviouslyCoded("codingAll")

    for d in coder_ref.obituaries:
        d['date'] = datetime.datetime.strptime(d['_date'], "%B %d, %Y")

    coder = occ.Coder()
    coder.loadPreviouslyCoded(db_to_match)

    for d in coder.obituaries:
        if d['id'] < 1000000:
            continue

        # match by name and date
        search1 = [
            x for x in coder_ref.obituaries
            if x['name'] == d['name'] and x['date'] == d['date']
        ]
        #search2 = [
        #    x for x in coder_ref.obituaries
        #    if x['date'] == d['date'] and (
        #        (set(x['firstSentence']) in set(d['firstSentence']))
        #        or (set(d['firstSentence']) in set(x['firstSentence']))
        #    )
        #]

        if len(search1) == 1:
            r = search1[0]

            print(d['firstSentence'])
            print(r['firstSentence'])
            print("------------------")
            print(r['id'])

            d['id'] = r['id']

    coder.dumpCodes(db_to_match)


if step==1:
    # relatively simple. if the first 100 characters have the same transition probabilities,
    # it's probably the same one...
    # I couldn't think of anything much better!

    from collections import Counter, defaultdict
    import datetime
    import numpy as np

    import occ, nlp

    N = None

    if True:
        coder_ref = occ.Coder()
        coder_ref.loadPreviouslyCoded("codingAll", N=N, rand=False)

        coder = occ.Coder()
        coder.loadPreviouslyCoded(db_to_match, N=N, rand=False)

    nmatch = 100

    def get_tupleCounter(body):
        word_length = 1
        nwords = 100
        words = [
            body[i:i+word_length]
            for i in range( min(len(body)//word_length, nwords) )
        ]
        # make even length, max 100 words!
        words = words[:nwords]
        words = words[:(len(words) // 2) * 2]

        return Counter(zip(words[::2], words[1::2]))

    def tupleCounterDifference(x, y):
        return sum( ((x-y) + (y-x)).values() )

    id_lookup = defaultdict(list)
    # segment by date, then by the body of the obit.
    for d in coder_ref.obituaries:
        d['date'] = datetime.datetime.strptime(d['_date'], "%B %d, %Y")

        tupleCounter = get_tupleCounter(d['fullBody'])
        id_lookup[d['date']].append( ( tupleCounter, d['id'] ) )

    id2doc = {
        d['id']: d
        for d in coder_ref.obituaries
    }

    nones = 0

    for i, d in enumerate(coder.obituaries):
        assert(isinstance(d, occ.Doc))

        if i % 100 == 0:
            print( "%s / %s" % (i, len(coder.obituaries)))

        # trying to figure out ID
        # current methods take too long!

        tupleCounter = get_tupleCounter(d['fullBody'])
        differences = [
            (
                tupleCounterDifference(x[0], tupleCounter),
                x[1]
            )
            for x in id_lookup[d['date']]
        ]
        if not len(differences):
            print("No lookup for date, ", d['date'])
            continue
        diff, id = min(differences, key=lambda x: x[0])

        #print("ID:",id, "(used to be ", d['id'], ")")
        #print("difference: %s" % diff)
        #print(d['firstSentence'])
        #print(id2doc[id]['firstSentence'])

        if diff > 40:
            id = 1000000 + nones
            nones += 1

        d['id'] = id

    print("Found the IDs of %s / %s successfully" % (nones, len(coder.obituaries)))

    coder.dumpCodes(db_to_match)