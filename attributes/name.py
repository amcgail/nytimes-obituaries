import g

class name(g.PropertyCoder):
    def run(self):
        if self['name_parts'] is None:
            return None

        parts = ['first', 'middle', 'last', 'suffix']
        getparts = [ self['name_parts'][x] for x in parts ]
        getparts = [ x for x in getparts if x != '' ]
        return " ".join(getparts)

class name_from_died_sent(g.PropertyCoder):
    """
    """

    def run(self):
        import nlp

        ds = self['died_sentence']
        if ds is None:
            return None

        who_died = []

        ds = nlp.spacy_parse(ds)

        # now find the died word...
        candidates = [x for x in ds if x.pos_ == 'VERB' and "die" == x.lemma_]

        for c in candidates:
            subjs = [x for x in c.children if x.dep_ == "nsubj"]
            for subj in subjs:
                noun_chunk = nlp.nc_from_word(ds, subj)
                if noun_chunk is not None:
                    who_died.append(noun_chunk)

            continue
            # skipping all of this -- probably not necessary
            conjs = [x for x in c.ancestors if x.dep_ == "conj"]
            subjs = [y for conj in conjs for y in conj.children if y.dep_ == "nsubj"]
            for subj in subjs:
                noun_chunk = nlp.nc_from_word(ds, subj)
                if noun_chunk is not None:
                    who_died.append(noun_chunk)

        return [ str(x) for x in who_died ]


class name_parts(g.PropertyCoder):
    """
    This is the core of the algorithm to extract name.
    It does so by the following:
        1. Extract name from the title_info
        2. Take whatever is before the first comma, or if this isn't reasonable (e.g. too many characters, or no comma),
            take the first noun chunk. If this is still not a name, discard this information.
        3. If the title's name and first sentence name "match", look no further.
        4. Otherwise, collect some candidate names, and search for the most common last name. Intelligently build from there.
        5. All these methods give many pseudonyms, which are also exported
    """

    def run(self):
        from nlp import HumanName
        import re
        from collections import Counter

        class someException(Exception):
            pass

        match_a = [
            self['title_info']['name'],
            re.split( r"[;,]", self['title'] )[0], # in case my title_info var isn't quite done...
            self['title']
        ]

        match_b = [
            self['firstSentence'].split(",")[0]
        ] + \
            self['stanford_PERSON'][:1] + \
              self['spacy_ents'][:1] + \
              self['spacy_noun_chunks'][:1] + \
        self['stanford_PERSON'] + self['spacy_noun_chunks']#+ [ str(x) for x in self['spacyFullBody'].noun_chunks ]

        def name_preprocessing(n):
            import re
            # C.V. Vanderbuilt ==> C. V. Vanderbuilt
            n = re.sub("\.([^\s])", r". \1", n)
            return n

        def name_filter(n):
            if n is None:
                return False
            if type(n) is not str:
                return False
            if len(n) < 5:
                return False
            if len(n.split()) < 2:
                return False
            if not all( ord("A") <= ord(x[0]) <= ord("Z") or x in ['van', 'de', 'von', 'der', 'la', 'abu'] for x in n.split() ):
                return False

            return True

        def extend_length(d_orig, d_extend):
            for k in d_extend:
                # fuck all caps (even with periods)
                numcaps = len(set(d_extend[k]).intersection(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")))
                if numcaps >= len(d_extend[k])-1 > 1 and False:
                    continue

                if k not in d_orig:
                    d_orig[k] = d_extend[k]
                else:
                    if len(d_extend[k]) > len(d_orig[k]):
                        d_orig[k] = d_extend[k]

        match_a = filter(name_filter, match_a)
        match_b = filter(name_filter, match_b)

        match_a = list(map( name_preprocessing, match_a ))
        match_b = list(map( name_preprocessing, match_b ))

        # print( match_a, match_b )

        fullThing = {
            'first': '',
            'last': '',
            'middle': '',
            'nickname': '',
            'suffix': '',
            'title': ''
        }

        # If there's no title to go off, just go in order, building the name as you go
        if len(match_a) == 0:

            self['name_method'] = "build_as_go"

            hns = [HumanName(x) for x in match_b]
            last_names = Counter( x.last for x in hns )
            top_lns = last_names.most_common(5)
            #print(top_lns)

            if len(top_lns) > 1 and top_lns[0][1] > top_lns[1][1]:
                top_ln = top_lns[0][0]

                for x in hns:
                    xdict = x.as_dict()
                    # the "not in" controls for crazy last names... "de Jesus Martinez" vs "Martinez"
                    if top_ln not in x.last:
                        continue
                    #print(x)

                    crappy = False
                    for k in fullThing:
                        if fullThing[k] == '':
                            continue

                        if xdict[k] == '':
                            continue

                        if fullThing[k] != xdict[k]:
                            crappy = True

                    if crappy:
                        continue

                    extend_length(fullThing, xdict)

                return fullThing
            else:
                return None

        else:

            self['name_method'] = "ab_match"

            # try to match the things!
            match = False
            for a in match_a:
                for b in match_b:
                    au = a.upper()
                    bu = b.upper()

                    a_uhn, b_uhn = HumanName(au), HumanName(bu)

                    if a_uhn.supercedes(b_uhn) or b_uhn.supercedes(a_uhn):
                        #print("Match")
                        #print(a,b)

                        for name in [a_uhn, b_uhn]:
                            extend_length(fullThing, name.as_dict())

                        match = True

                    if au in bu or bu in au:
                        #print("Substring match")
                        #print(a,b)

                        if au in bu:
                            extend_length(fullThing, a_uhn.as_dict())
                        else:
                            extend_length(fullThing, b_uhn.as_dict())

                        match = True

                    if match:
                        break

                if match:
                    break

            if not match:
                return None
            else:
                return fullThing

        return None


        name_votes.append(simplest)
        name_votes += [most_common]
        name_votes.append( tname )



        name_votes.append(self['spacyName'])

        name_votes = list(filter(lambda x: x is not None, name_votes))
        name_votes = list(filter(lambda x: len(x.split()) <= 5, name_votes))

        #print(name_votes)

        def extend_length(d_orig, d_extend):
            for k in d_extend:

                # fuck all caps (even with periods)
                numcaps = len(set(d_extend[k]).intersection(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")))
                if numcaps >= len(d_extend[k])-1 > 1:
                    continue

                if k not in d_orig:
                    d_orig[k] = d_extend[k]
                else:
                    if len(d_extend[k]) > len(d_orig[k]):
                        d_orig[k] = d_extend[k]

        # if we're left with nothing, we can't make a decision
        if len(name_votes) == 0:
            return None

        # have them vote
        lname_true = g.sensibleVote( HumanName(x).last.lower() for x in name_votes)
        name_true = g.sensibleVote( ( HumanName(x).first.lower(), HumanName(x).last.lower() ) for x in name_votes if HumanName(x).last.lower() == lname_true )

        if name_true is None:
            return None

        return fullThing

    def run_2(self):
        from nlp import HumanName
        from collections import Counter

        name_votes = []

        sname = HumanName( str(self['spacyName']).strip() )
        most_common = HumanName( self['name_by_most_common'] )
        name_votes += [sname, most_common]

        tname = self['title_info']['name']
        if tname is not None:
            tname = HumanName( tname )
            name_votes.append( tname )

        simplest = HumanName( self['firstSentence'].split(",")[0] )
        name_votes.append(simplest)

        # I'm just going to do a simple vote!
        versions = [
            x.as_dict() for x in name_votes
        ]

        keys = versions[0].keys()

        final = {}
        for k in keys:
            votes = [ v[k] for v in versions if v[k].strip() != "" ]
            if not len(votes):
                continue

            votes = Counter( votes )
            topvote = votes.most_common(1)[0][0]
            final[k] = topvote

        return final

class name_by_most_common(g.PropertyCoder):
    def run(self):
        from nlp import isPossibleFullName, HumanName
        from functools import partial
        from collections import Counter

        all_possible_names = self['stanford_PERSON']
        all_possible_names = list(map(HumanName, all_possible_names))

        possible_full_names = self['stanford_PERSON']
        possible_full_names = list(filter(isPossibleFullName, possible_full_names))
        possible_full_names = list(map(HumanName, possible_full_names))

        def custom_supercede_relation(big, small):
            if len(small.original.split()) <= 1:
                # either first or last name match adds to count
                return small.original in [big.last, big.first]
            else:
                return big.supercedes(small)

        counts = {}
        for fname in possible_full_names:
            c = len(list(filter(partial(custom_supercede_relation, fname), all_possible_names)))
            counts[fname.original] = c

        # print(counts)

        if len(counts) == 0:
            return None

        bestCount = max(counts.values())

        # if there's a tie for first, return None
        if Counter(counts.values())[bestCount] > 1:
            return None

        return [ name for name, count in counts.items() if count == bestCount][0]

class human_name(g.PropertyHelper):

    def run(self):
        import nlp
        if self['name'] is None:
            return None

        return nlp.HumanName(self.ofWhat["name"])


class first_name(g.PropertyCoder):


    def run(self):
        if self['name'] is not None:
            return self.ofWhat['human_name'].first
        else: return None


class last_name(g.PropertyCoder):


    def run(self):
        if self['name'] is not None:
            return self.ofWhat['human_name'].last
        else: return None

class spacyName(g.PropertyHelper):
    """
    This function was our original method of finding the name.
    It starts by using named entity recognition from Spacy,
        and if a name is in the first sentence, it returns the first one.

    It then just looks for all "noun chunks" which sometimes expands this set

    If that fails, it returns "<name not found>"
    """

    def run_old(self):
        import nlp
        ret = None

        # print(self.ofWhat['firstSentence'])
        # most consistently, it's the first noun chunk:
        def isName(x):
            if len(x.split()) < 2:
                return False
            if not nlp.isTitleCase(x):
                return False
            return True

        # start with NER from spacy:
        if ret is None:
            guesses = self.ofWhat['spacyFirstSentence'].ents
            guesses = [x for x in guesses if x.label_ == 'PERSON' and isName(x.text)]
            if len(guesses) > 0:
                # just use the first one
                # and we'll probably need expansion
                ret = guesses[0].text
                # print("NER for the win")

        # first, expand. it many times doesn't get parens, or Dr. Rev. etc.
        # we then need to look deeper, if it's a "Mr." "Mrs." or "Dr."

        # then just try some noun chunking...
        if ret is None:
            nc = list(self.ofWhat['spacyFirstSentence'].noun_chunks)
            if len(nc) > 0:
                nc = list(filter(isName, map(str, nc)))
                if len(nc) > 0:
                    ret = nc[0]
                    # print("Noun Chunk Found!")

        if ret is None:
            ret = None
        return ret
        # print(name)

        if False:
            # try spacy's NER:
            guesses = self.ofWhat['spacyFirstSentence'].ents
            guesses = [x for x in guesses if x.label_ == 'PERSON']
            print("FS:", self.ofWhat['firstSentence'])
            if len(guesses) > 0:
                print("Found:", [x.text for x in guesses])

        if True:
            # name is ALMOST ALWAYS the first noun_chunk.
            nc = list(self.ofWhat['spacyFirstSentence'].noun_chunks)
            if len(nc) > 0:
                nc = list(filter(nlp.isTitleCase, map(str, nc)))
                if len(nc) > 0:
                    # print(nc)
                    pass
                # print("FS:", self.ofWhat['firstSentence'])
            return

            # also could just check that the words are in the title...
            if fsname is not None:
                t = self.ofWhat['title'].lower()
                tw = set(nlp.word_tokenize(t))
                fsnamew = set(nlp.word_tokenize(str(fsname).lower()))
                if len(tw.intersection(fsnamew)) > 0:
                    # print(fsname)
                    pass

            # the title is a good check
            if False:
                tname = self.ofWhat['title']
                pats = [
                    "is dead",
                    ",",
                    "dies",
                    "is slain",
                    "of",
                    "dead",

                ]
                for pat in pats:
                    tname = re.split(pat, tname, flags=re.IGNORECASE)[0]

    def run(self):
        if self['name'] is None:
            return None

        from nlp import HumanName
        nc = self['spacyFirstSentence'].noun_chunks

        humanName = HumanName(self['name'].lower())

        for possibleName in nc:
            if humanName.last in possibleName.string.lower():
                #print(x)
                return possibleName

        return None