import g


def check_phrase_for_occupations(s):
    import nlp
    from occ import set2code

    found = []

    words = nlp.word_tokenize(s)
    words = [nlp.lemmatize(x) for x in words]

    sets = set()
    sets.update(nlp.getCloseUnorderedSets(words, minTuple=1, maxTuple=1, maxBuffer=0))
    sets.update(nlp.getCloseUnorderedSets(words, minTuple=2, maxTuple=2, maxBuffer=1))
    sets.update(nlp.getCloseUnorderedSets(words, minTuple=3, maxTuple=3, maxBuffer=2))
    #sets.update(nlp.getCloseUnorderedSets(words, minTuple=4, maxTuple=4, maxBuffer=2))

    for fs in sets:
        if fs in set2code:
            c = set2code[fs]["code"]

            found.append({
                "word": " ".join(fs),
                "occ": [c],
                "fs": fs
            })

    def is_subset_anyone(x):
        for y in found:
            if x['fs'] != y['fs'] and x['fs'].issubset(y['fs']):
                return True

    found = [x for x in found if not is_subset_anyone(x)]

    return found

def check_phrase_for_occupations_nobreaks(s):
    import nlp
    from occ import set2code

    found = []

    words = nlp.word_tokenize(s)
    words = [nlp.lemmatize(x) for x in words]

    sets = set()
    sets.update(nlp.getCloseUnorderedSets(words, minTuple=1, maxTuple=1, maxBuffer=0))
    sets.update(nlp.getCloseUnorderedSets(words, minTuple=2, maxTuple=2, maxBuffer=0))
    sets.update(nlp.getCloseUnorderedSets(words, minTuple=3, maxTuple=3, maxBuffer=0))
    sets.update(nlp.getCloseUnorderedSets(words, minTuple=4, maxTuple=4, maxBuffer=0))

    for fs in sets:
        if fs in set2code:
            c = set2code[fs]["code"]

            found.append({
                "word": " ".join(fs),
                "occ": [c],
                "fs": fs
            })

    def is_subset_anyone(x):
        for y in found:
            if x['fs'] != y['fs'] and x['fs'].issubset(y['fs']):
                return True

    found = [x for x in found if not is_subset_anyone(x)]

    return found


class OCC(g.PropertyCoder):

    def run(self):
        from itertools import chain

        full_name = self['name']

        fs = self.ofWhat["firstSentence"].lower()
        ttl = self.ofWhat["title"].lower()

        if full_name is not None:
            fs = fs.replace(full_name, "")
            ttl = ttl.replace(full_name, "")

        found_first = check_phrase_for_occupations(fs)
        found_title = check_phrase_for_occupations(ttl)

        # we want to keep track of "where"
        [x.update({"where": "firstSentence"}) for x in found_first]
        [x.update({"where": "title"}) for x in found_title]

        return found_first + found_title
        #return list(set(chain.from_iterable(x['occ'] for x in found_first + found_title)))

class OCC_titleSyntaxU(g.PropertyCoder):
    def run(self):
        from itertools import chain
        if self['OCC_title'] is not None:
            print(self['OCC_title'])
            titleOCC = set( chain.from_iterable( [x['occ'] for x in self['OCC_title']] ) )
        else:
            titleOCC = set()

        if self['OCC_syntax'] is not None:
            syntaxOCC = set( x['code'] for x in self['OCC_syntax'] )
        else:
            syntaxOCC = set()

        return list( titleOCC.union( syntaxOCC ) )

class OCC_titleSyntaxI(g.PropertyCoder):
    def run(self):
        from itertools import chain
        if self['OCC_title'] is not None:
            print(self['OCC_title'])
            titleOCC = set( chain.from_iterable( [x['occ'] for x in self['OCC_title']] ) )
        else:
            titleOCC = set()

        if self['OCC_syntax'] is not None:
            syntaxOCC = set( x['code'] for x in self['OCC_syntax'] )
        else:
            syntaxOCC = set()

        return list( titleOCC.intersection( syntaxOCC ) )

class OCC_fullBody(g.PropertyCoder):

    def run(self):
        full_name = self['name']

        fb = self["fullBody"].lower()
        if full_name is not None:
            fb = fb.replace(full_name, "")

        found_fb = check_phrase_for_occupations_nobreaks(fb)

        # we want to keep track of "where"
        [x.update({"where": "fullBody"}) for x in found_fb]

        return found_fb
        #return list(set(chain.from_iterable(x['occ'] for x in found_first + found_title)))


class OCC_FsT_nobreaks(g.PropertyCoder):

    def run(self):
        from itertools import chain

        full_name = self['name']

        fs = self.ofWhat["firstSentence"].lower()
        ttl = self.ofWhat["title"].lower()

        if full_name is not None:
            fs = fs.replace(full_name, "")
            ttl = ttl.replace(full_name, "")

        found_first = check_phrase_for_occupations_nobreaks(fs)
        found_title = check_phrase_for_occupations_nobreaks(ttl)

        # we want to keep track of "where"
        [x.update({"where": "firstSentence"}) for x in found_first]
        [x.update({"where": "title"}) for x in found_title]

        return found_first + found_title
        #return list(set(chain.from_iterable(x['occ'] for x in found_first + found_title)))


class _OLDEROCC(g.OldPropertyCoder):


    def run(self):
        def check(s):
            import nlp
            from occ import term2code
            found = []

            words = nlp.word_tokenize(s.lower())
            words += ["-"] + nlp.word_tokenize(s.lower())

            # This algorithm proceeds from largest to smallest tuples, making sure not to count any codes inside codes

            max_tuples = 4
            current_tuples = max_tuples

            process_now = nlp.getTuples(words, minTuple=4, maxTuple=4)

            while current_tuples > 0:
                # print(process_now, current_tuples)

                dont_process_next = set()

                for tup in process_now:
                    tocheck = " ".join(tup)
                    if tocheck in term2code:
                        c = term2code[tocheck]["code"]
                        found.append({
                            "word": tocheck,
                            "occ": [c]
                        })

                        dont_process_next.update(nlp.getTuples(
                            list(tup),
                            minTuple=current_tuples - 1,
                            maxTuple=current_tuples - 1
                        ))

                # print(dont_process_next)

                process_now = set(nlp.getTuples(
                    words,
                    minTuple=current_tuples - 1,
                    maxTuple=current_tuples - 1
                ))
                process_now = process_now.difference(dont_process_next)

                current_tuples -= 1

            return found

        found_first = check(self.ofWhat["firstSentence"])
        found_title = check(self.ofWhat["title"])

        # we want to keep track of "where"
        [x.update({"where": "firstSentence"}) for x in found_first]
        [x.update({"where": "title"}) for x in found_title]

        return found_first + found_title


class OCC_wikidata(g.PropertyCoder):
    def run(self):
        import wiki
        dead_guys_occs = []

        if self['name'] is not None:
            words = wiki.lookupOccupationalTitles(self["name"])
            for x in words:
                dead_guys_occs.append( check_phrase_for_occupations(x) )

            if len(dead_guys_occs) > 0:
                if self.debug:
                    g.p("WikiData returns %s which gives OCC %s" % (words, dead_guys_occs))
        else:
            return None

        return dead_guys_occs

class OCC_title(g.PropertyCoder):
    def run(self):
        import nlp

        # extract information from the title
        d1 = self['title_info']['desc']
        d2 = self['title_info']['desc2']

        if d1 is None and d2 is None:
            return None

        found = []

        if d1 is not None:
            d1 = d1.lower()

            if self['name'] is not None:
                name = self['name'].lower()
                d1 = d1.replace(name, "")

            found += check_phrase_for_occupations(d1)

        if d2 is not None:
            d2 = d2.lower()

            if self['name'] is not None:
                name = self['name'].lower()
                d2 = d2.replace(name, "")

            found += check_phrase_for_occupations(d2)

        return found


class OCC_syntax(g.PropertyCoder):

    def run(self):
        import g
        from occ import set2code
        import nlp
        import wiki
        import re

        didSomething = False

        if self['spacyName'] is None:
            return None

        guesses = []

        # Alec McGail, scientist and genius, died today.
        nameChildren = list(self["spacyName"].root.children)
        apposHooks = list(filter(lambda nameChild: nameChild.dep_ == 'appos', nameChildren))

        if len(apposHooks) > 0:
            didSomething = True

            # painter, scientist, and architect
            baseNouns = nlp.followRecursive(apposHooks, 'conj')

            # one of the first **novelists**
            for i, x in enumerate(baseNouns):
                if nlp.isPrepPhrase(x) and str(x) == 'one':
                    entered = nlp.enterPrepPhrase(x)
                    if not len(entered):
                        continue

                    baseNouns[i] = entered[0]

            # now that the important "what they were" nouns are identified,
            #   identify what OCC they are
            for n in baseNouns:
                n = frozenset([str(n)])
                print("searching for", n)
                if n in set2code:
                    result = set2code[n]
                    guesses.append(result)

        return guesses

        # Alec McGail, who ..., died today.
        relcls = list(filter(lambda nameChild: nameChild.dep_ == 'relcl', nameChildren))

        if len(relcls) > 0:
            g.p.depth += 1

        for relcl in relcls:
            # need to follow advcl and conj
            goDeep = nlp.followRecursive(relcl, ['advcl', 'conj'])
            be = ['was', 'became']
            for v in goDeep:
                # as _
                followPreps = nlp.followRecursive(v, ['relcl', 'prep', 'pobj'])
                asWhat = [x for x in followPreps if next(x.ancestors).text == 'as' and x.pos_ == 'pobj']

                if self.debug and len(asWhat):
                    g.p('whoAs', asWhat)

                if len(asWhat):
                    didSomething = True

                # who was a scientist and inventor
                if v.pos_ == 'VERB':
                    if v.text in be:
                        for vc in v.children:
                            if vc.dep_ != 'attr':
                                continue

                            if self.debug:
                                g.p('Expanded be verb', vc, vc.dep_)

                            # guesses.append(result)
                            didSomething = True

        finalGuess = []
        for guess in guesses:
            if len(guess['occ']) != 1:
                continue
            finalGuess.append(guess['occ'][0])

        if self.debug:
            g.p("finalGuess", finalGuess)

        if False:
            moreGuesses = []
            # more stupid guesses...
            # literally expand every noun

            for w in self.ofWhat['spacyFirstSentence']:
                if w.pos_ != 'NOUN':
                    continue
                guess = coding.nounOCC(w)
                moreGuesses.append(guess)

            stupidFinalGuess = []
            for guess in moreGuesses:
                stupidFinalGuess += guess['occ']

            if self.debug:
                g.p("stupidFinalGuess", stupidFinalGuess)

                if set(stupidFinalGuess) != set(finalGuess):
                    g.p("And they're different!", extrad=1)

        if not didSomething:
            if len(dead_guys_occs) > 0:
                coding.stateCounter.update(["justWikidata"])
            else:
                if self.debug:
                    g.p("Skipping. Strange grammatical construction.")
                coding.stateCounter.update(["strangeGrammar"])



class _WAITOCC_weighted(g.OldPropertyCoder):

    def run(self):
        import nlp
        from collections import Counter
        from occ import term2code

        fS = self.ofWhat["firstSentence"]
        name = self.ofWhat["name"]

        allCodes = []

        wasDidC = []
        wasDidC += nlp.bagOfWordsSearch(self.ofWhat["whatTheyDid"], term2code)
        wasDidC += nlp.bagOfWordsSearch(self.ofWhat["whatTheyWere"], term2code)

        for x in wasDidC:
            allCodes.append({
                "where": "wasDid",
                "word": x['term'],
                "occ": x['code']
            })

        def justCodes(l):
            return [x['code'] for x in l]

        wasDidC = Counter(justCodes(wasDidC))
        fsC = Counter(justCodes(nlp.tupleBaggerAndSearch(fS, term2code)))
        f500C = Counter(justCodes(nlp.tupleBaggerAndSearch(self.ofWhat['_first500'], term2code)))
        bodyC = Counter(justCodes(nlp.tupleBaggerAndSearch(self.ofWhat['_fullBody'], term2code)))

        weightedC = {}
        w = {}
        w['did'] = 5
        w['fS'] = min(1, 6 * 10. / len(fS)) if len(fS) > 0 else 1
        w['f500'] = 0.5 * 6 * 10. / 500
        w['body'] = min(0.1, 0.1 * 6 * 10. / len(self.ofWhat['_fullBody'])) if len(self.ofWhat['fullBody']) > 0 else 1

        # print w
        for x in set( list(fsC.keys()) + list(f500C.keys()) + list(bodyC.keys())):
            weightedC[x] = wasDidC[x] * w['did'] + fsC[x] * w['fS'] + f500C[x] * w['f500'] + bodyC[x] * w['body']

        # this is the confidence of our favorite...
        confidence = max(weightedC.values()) if len(weightedC) > 0 else -1

        # order list by the confidences...
        rankedC = sorted(weightedC.items(), key=lambda item: -item[1])

        # and take the top 3
        topC = rankedC[:3]
        topC = [list(x) for x in topC]

        # then idk do something...