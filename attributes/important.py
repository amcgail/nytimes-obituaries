import g


"""
# this is parsed by previous shit

class date(g.PropertyCoder):


    def run(self):
        import datetime
        return datetime.datetime.strptime(self.ofWhat['_date'], "%B %d, %Y")
"""

class died_sentence(g.PropertyCoder):
    def run(self):

        from nlp import sent_tokenize, word_tokenize, lemmatize
        fb = self['fullBody']

        possibilities = sent_tokenize(fb)

        for i, p in enumerate(possibilities):
            words = word_tokenize(fb)
            words = map(lemmatize, words)
            if len( [x for x in words if x == 'die'] ):
                return p

class lexicalAttributes(g.PropertyCoder):

    def run(self):
        import nlp
        return nlp.extractLexical(self.ofWhat["spacyFullBody"], self.ofWhat["name"])

class kinship(g.PropertyCoder):
    """
    Just some test documentation.
    This should describe what this property coder does...
    """

    def run(self):
        import nlp

        my_props = set()

        toSearch = self.ofWhat['firstSentence']

        # don't want lexicon (or a name) to be spotted in the "died on the 3rd with is family"
        toSearch = toSearch.split("died")[0]
        toSearch = toSearch.split("dead")[0]
        toSearch = toSearch.split("killed")[0]
        toSearch = toSearch.split("drowned")[0]

        # their own name might get confusing for this analysis...
        toSearch = toSearch.replace(self.ofWhat["name"], "")

        # intelligent tokenization
        toSearchWords = nlp.word_tokenize(toSearch)

        kinMatch = 0
        kinMatchStronger = 0

        lexicon = nlp.inquirer_lexicon["KIN"]

        for x in toSearchWords:
            if x.upper() in lexicon:
                kinMatch += 1
        for x in nlp.getTuples(toSearchWords, 2, 2):
            if x[0].upper() in lexicon and x[1].upper() == "OF":
                kinMatchStronger += 1

        if kinMatch > 0:
            my_props.add("lex_match")
        if kinMatchStronger > 0:
            my_props.add("lex_match_strong")

        # I also need a full name that matches in the last name...
        for names in nlp.getTuples(toSearchWords, 2, 3):
            # must be capitalized...
            if any(x[0].lower() == x[0] for x in names):
                continue

            # last must be the same name!
            if names[-1].lower() != self.ofWhat["last_name"]:
                continue

            my_props.add("name_match")
            break

        return list(my_props)


class proper_nouns(g.PropertyCoder):


    def run(self):
        ret = []

        for chunk in self.ofWhat['spacyFullBody'].noun_chunks:

            # ch = chunk.text
            # ch.replace("\n", " ")
            # ch.replace("  ", " ")
            # ch = ch.strip()

            if chunk.text == chunk.text.lower():
                continue

            # words that aren't spaces...
            chunk = list(chunk)
            chunk = [x for x in chunk if x.pos_ != 'SPACE']

            # expand if necessary
            nextWord = chunk[-1]
            if nextWord.i + 1 < len(nextWord.doc):
                nextWord = nextWord.doc[nextWord.i + 1]

                # if it has capitalization, keep going.
                while str(nextWord).lower() != str(nextWord) or nextWord.pos_ == 'SPACE':
                    # skip spaces...
                    if nextWord.pos_ != 'SPACE':
                        chunk.append(nextWord)

                    if nextWord.i + 1 >= len(nextWord.doc):
                        break

                    nextWord = nextWord.doc[nextWord.i + 1]

            # turn the chunk into a string.
            ch = " ".join([str(w) for w in chunk])

            ret.append(ch)

        return ret




class whatTheyWere(g.PropertyCoder):


    def run(self):
        return self.ofWhat["lexicalAttributes"]["was"]


class whatTheyDid(g.PropertyCoder):


    def run(self):
        return self.ofWhat["lexicalAttributes"]["did"]


class nouns(g.PropertyCoder):


    def run(self):
        doc = self.ofWhat["spacyFullBody"]

        ret = []
        for x in doc:
            if x.pos_ == "NOUN":
                ret.append(str(x))
        return ret


class adjectives(g.PropertyCoder):


    def run(self):
        doc = self.ofWhat["spacyFullBody"]

        ret = []
        for x in doc:
            if x.pos_ == "ADJ":
                ret.append(str(x))
        return ret


class verbs(g.PropertyCoder):


    def run(self):
        doc = self.ofWhat["spacyFullBody"]

        ret = []
        for x in doc:
            if x.pos_ == "VERB":
                ret.append(str(x))
        return ret


class gender(g.PropertyCoder):


    def run(self):
        import nlp
        fn_guess = nlp.gender_detector.get_gender(self["first_name"])

        male = nlp.inquirer_lexicon.countWords("MALE", self['fullBody'])
        female = nlp.inquirer_lexicon.countWords("Female", self['fullBody'])

        # if the results are unconclusive from this simple check:
        if male + female < 4 or abs(male - female) / (male + female) < 0.25:
            # guess = nlp.gender_detector.get_gender(self.ofWhat["first_name"])
            if fn_guess in ["male", "female"]:
                return fn_guess

            # if this even didn't work!
            return "unknown"

        # at this point we know that there are enough pronouns to make an educated guess
        if male > female:
            return "male"
        return "female"


class spacyFullBody(g.PropertyHelper):


    def run(self):
        import nlp
        return nlp.spacy_parse(self.ofWhat['fullBody'])


class firstSentence(g.PropertyCoder):


    def run(self):
        from nlp import extractFirstSentence
        return extractFirstSentence(self.ofWhat['fullBody']).strip()


class spacyFirstSentence(g.PropertyHelper):


    def run(self):
        import nlp
        return nlp.spacy_parse(self.ofWhat["firstSentence"])



class date_of_death(g.PropertyCoder):

    def isDied(self, x):
        return x.string.strip() in ["died", "killed"]

    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    def run(self):
        from datetime import timedelta

        from dateutil import parser

        import occ
        import nlp

        ds = self['died_sentence']

        if ds is None:
            # print("NO DIED SENT: ", obit['firstSentence'])
            return None

        if "died" not in ds:
            # print("SKIPPED: ", ds)
            return None

        ds = nlp.spacy_parse(ds)
        died_words = list(filter(self.isDied, ds))

        if not len(died_words):
            # print("NO DIED WORD")
            return None

        possibles = set()

        mods = [x for x in died_words[0].children if x.dep_ == 'npadvmod']
        if len(mods):
            possibles.update(set(" ".join(y.string.strip() for y in x.subtree) for x in mods))

        preps = [x for x in died_words[0].children if x.dep_ == 'prep']
        for p in preps:
            if p.string.strip() != "on":
                continue

            root = list(p.children)[0]
            possibles.add(" ".join(y.string.strip() for y in root.subtree))

        # print( "OBITDATE", self['date'] )
        # print( self['firstSentence'] )
        # print(possibles)

        for p in possibles:
            p = p.strip()

            if p.lower() in ["this morning", "this afternoon", "this evening"] or \
                    "today" in p.lower():
                return self['date']

            if p.lower() in ["last night"] or "yesterday" in p.lower():
                return self['date'] - timedelta(days=1)

            for dowi, dow in enumerate(self.days_of_week):
                if dow in p.lower():
                    obitw = self['date'].weekday()
                    deathw = dowi

                    if obitw > deathw:
                        return self['date'] - timedelta(days=obitw - deathw)
                    else:
                        return self['date'] - timedelta(days=7 + obitw - deathw)

            # what if it's a full date?
            try:
                dt = parser.parse(p)

                if abs(dt.year - self['date'].year) > 1:
                    dt = dt.replace(year=self['date'].year)

                while dt > self['date']:
                    dt = dt.replace(year=dt.year - 1)

                return dt
            except ValueError:
                pass

        # print( ds.split("died")[1] )
        # print("-----------------------------")


class age(g.PropertyCoder):


    def run(self):
        import g
        import re
        g.p.pdepth = 0

        lastName = self.ofWhat["name"].split()[-1]

        rgxs = [
            r"(?:Mr\.?|Mrs\.?)\s*%s\s*was\s*([0-9]{1,3})(?:\s*years\s*old)?" % re.escape(lastName),
            r"(?:She|He)\s*was\s*([0-9]{1,3})(?:\s*years\s*old)?",
            r"died.*at\s+the\s+age\s+of\s+([0-9]{1,3})",
            r"was\s*([0-9]{1,3})\s*years\s*old",
            r"was\s*([0-9]{1,3})",
            r"([0-9]{1,3})\s*years\s*old",
            r"was\s*believed\s*to\s*be([^,\.]*)",
            r"was\s*in\s*(?:his|her)\s*([^,\.]*)",
            r"([0-9]{1,3})",
        ]

        sents = list(self.ofWhat['spacyFullBody'].sents)

        foundReasonableAge = False
        # look for these sentences, in order
        for rgx in rgxs:
            for s in sents:
                fAge = re.findall(rgx, s.text)
                if len(fAge) == 0:
                    continue

                for sAge in fAge:
                    try:
                        age = int(sAge)
                        if age > 120 or age < 5:
                            continue

                        foundReasonableAge = True
                        break
                    except ValueError:
                        continue

                if foundReasonableAge:
                    break

            if foundReasonableAge:
                break

        if foundReasonableAge:
            return age