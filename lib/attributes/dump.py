from g import PropertyCoder, PropertyHelper, OldPropertyCoder

class lexicalAttributes(PropertyCoder):

    def run(self):
        import nlp
        return nlp.extractLexical(self.ofWhat["spacyFullBody"], self.ofWhat["name"])

class _OLDEROCC(OldPropertyCoder):


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


class OCC_syntax(OldPropertyCoder):

    def run(self):
        import g
        from occ import set2code
        import nlp
        import wiki
        import re
        """
        if len(self.ofWhat['spacyFirstSentence']) == 0:
            if self.debug:
                g.p("Skipping. No content after trim.")
            coding.stateCounter.update(["zeroLengthSkip"])
            return

        if self.debug:
            g.p.depth = 0
            g.p()
            g.p(self.ofWhat['spacyFirstSentence'])

            g.p.depth += 1
        """

        dead_guys_occs = set()

        if len(self.ofWhat["name"]) > 0:
            words = wiki.lookupOccupationalTitles(self.ofWhat["name"])
            for x in words:
                dead_guys_occs.update(set2code[set(x)])

            if len(dead_guys_occs) > 0:
                if self.debug:
                    g.p("WikiData returns %s which gives OCC %s" % (words, dead_guys_occs))

        if self.debug:
            g.p("Extracted name: %s" % self.ofWhat["name"])

        # extract information from the title
        dieWords = ['dies', 'die', 'dead']
        t = self.ofWhat['title']
        ts = [x.strip() for x in re.split(r'[;,]|--', t)]
        ts = ts[1:]  # the name is always the first one

        for tp in ts:
            tpW = [x.lower() for x in nlp.word_tokenize(tp)]
            hasDeathWord = False
            for dW in dieWords:
                if dW in tpW:
                    hasDeathWord = True
            if hasDeathWord:
                continue

            # if it's a number, continue
            try:
                int(tp)
                continue
            except ValueError:
                pass

            if self.debug:
                g.p("Extracted from title:", tp)

        didSomething = False

        guesses = []

        # Alec McGail, scientist and genius, died today.
        nameChildren = list(self.ofWhat["spacyName"].root.children)
        apposHooks = list(filter(lambda nameChild: nameChild.dep_ == 'appos', nameChildren))

        if len(apposHooks) > 0:
            didSomething = True

            # painter, scientist, and architect
            baseNouns = nlp.followRecursive(apposHooks, 'conj')

            # one of the first **novelists**
            for i, x in enumerate(baseNouns):
                if nlp.isPrepPhrase(x) and str(x) == 'one':
                    baseNouns[i] = nlp.enterPrepPhrase(x)[0]

            # now that the important "what they were" nouns are identified,
            #   identify what OCC they are
            for n in baseNouns:
                result = set2code[set(n)]
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



class _WAITOCC_weighted(OldPropertyCoder):


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
