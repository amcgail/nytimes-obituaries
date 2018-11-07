from g import PropertyCoder, PropertyHelper

# the following two are no longer used
class title(PropertyCoder):


    def run(self):
        t = self.ofWhat['_title']
        t = t.split("\n")[-1].strip()  # gets rid of those gnarly prefixes
        return t


class date(PropertyCoder):


    def run(self):
        import datetime
        return datetime.datetime.strptime(self.ofWhat['_date'], "%B %d, %Y")



class spacyName(PropertyHelper):

    def run(self):
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
            ret = "<name not found>"
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

class kinship(PropertyCoder):

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

        return my_props


class proper_nouns(PropertyCoder):


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




class whatTheyWere(PropertyCoder):


    def run(self):
        return self.ofWhat["__extractLexical"]["was"]


class whatTheyDid(PropertyCoder):


    def run(self):
        return self.ofWhat["__extractLexical"]["did"]


class nouns(PropertyCoder):


    def run(self):
        doc = self.ofWhat["spacyFullBody"]

        ret = []
        for x in doc:
            if x.pos_ == "NOUN":
                ret.append(str(x))
        return ret


class verbs(PropertyCoder):


    def run(self):
        doc = self.ofWhat["spacyFullBody"]

        ret = []
        for x in doc:
            if x.pos_ == "VERB":
                ret.append(str(x))
        return ret


class OCC(PropertyCoder):


    def run(self):
        from itertools import chain

        full_name = self.ofWhat['name']

        def check(s):
            import nlp
            from occ import set2code

            found = []

            s = s.replace(full_name, "")

            words = nlp.word_tokenize(s)
            words = [nlp.lemmatize(x) for x in words]

            sets = set()
            sets.update(nlp.getCloseUnorderedSets(words, minTuple=1, maxTuple=1, maxBuffer=0))
            sets.update(nlp.getCloseUnorderedSets(words, minTuple=2, maxTuple=2, maxBuffer=1))
            sets.update(nlp.getCloseUnorderedSets(words, minTuple=3, maxTuple=3, maxBuffer=2))
            sets.update(nlp.getCloseUnorderedSets(words, minTuple=4, maxTuple=4, maxBuffer=2))

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

        found_first = check(self.ofWhat["firstSentence"].lower())
        found_title = check(self.ofWhat["title"].lower())

        # we want to keep track of "where"
        [x.update({"where": "firstSentence"}) for x in found_first]
        [x.update({"where": "title"}) for x in found_title]

        return set(chain.from_iterable(x['occ'] for x in found_first + found_title))




class gender(PropertyCoder):


    def run(self):
        import nlp
        fn_guess = nlp.gender_detector.get_gender(self.ofWhat["first_name"])

        male = nlp.inquirer_lexicon.countWords("MALE", self.ofWhat['fullBody'])
        female = nlp.inquirer_lexicon.countWords("Female", self.ofWhat['fullBody'])

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


class name(PropertyCoder):


    def run(self):
        return str(self.ofWhat['spacyName']).strip()


class human_name(PropertyCoder):


    def run(self):
        import nlp
        return nlp.HumanName(self.ofWhat["name"])


class first_name(PropertyCoder):


    def run(self):
        return self.ofWhat['human_name'].first


class last_name(PropertyCoder):


    def run(self):
        return self.ofWhat['human_name'].last



class spacyFullBody(PropertyCoder):


    def run(self):
        import nlp
        return nlp.spacy_parse(self.ofWhat['fullBody'])


class firstSentence(PropertyCoder):


    def run(self):
        from occ import extractFirstSentence
        return extractFirstSentence(self.ofWhat['fullBody']).strip()


class spacyFirstSentence(PropertyHelper):


    def run(self):
        import nlp
        return nlp.spacy_parse(self.ofWhat["firstSentence"])


class age(PropertyCoder):


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
