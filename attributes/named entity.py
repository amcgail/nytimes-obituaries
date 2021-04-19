import g

# NER training and other materials:
# https://towardsdatascience.com/a-review-of-named-entity-recognition-ner-using-automatic-summarization-of-resumes-5248a75de175

# interface to stanford tagger:


# interface to stanford parser:
# http://projects.csail.mit.edu/spatial/Stanford_Parser

class spacy_ents(g.PropertyCoder):
    def run(self):
        return [ (ent.label_, ent.string) for ent in self['spacyFullBody'].ents ]

def filter_ents(what, ents):
    f = filter(lambda x: x[0] == what, ents)
    f = map(lambda x: x[1], f)
    return list(f)

class spacy_ents_PERSON(g.PropertyCoder):
    def run(self):
        return filter_ents("PERSON", self['spacy_ents'])

class spacy_ents_GPE(g.PropertyCoder):
    def run(self):
        return filter_ents("GPE", self['spacy_ents'])

class spacy_ents_NORP(g.PropertyCoder):
    def run(self):
        return filter_ents("NORP", self['spacy_ents'])

class spacy_ents_ORG(g.PropertyCoder):
    def run(self):
        return filter_ents("ORG", self['spacy_ents'])

class spacy_noun_chunks(g.PropertyCoder):
    def run(self):
        return [ str(x) for x in self['spacyFullBody'].noun_chunks ]

class stanford_fullBody_3(g.PropertyHelper):
    from nlp import nerConnection
    st = nerConnection()

    def run(self):
        from nltk import word_tokenize
        return self.st.tag(word_tokenize(self['fullBody']))

class stanford_LOCATION(g.PropertyCoder):
    def run(self):
        tags = self['stanford_fullBody_3']

        locations = []

        # merge consecutive
        current_loc = ""
        for text,tag in tags:
            if tag == 'LOCATION':
                if current_loc != "":
                    current_loc += " "
                current_loc += text
            else:
                if text == "," and current_loc != "":
                    current_loc += text
                else:
                    if current_loc != "":
                        locations.append(current_loc)
                        current_loc = ""

        if current_loc != "":
            locations.append(current_loc)

        return locations

class stanford_PERSON(g.PropertyCoder):
    def run(self):
        tags = self['stanford_fullBody_3']

        people = []

        # merge consecutive
        current_pers = ""
        for text,tag in tags:
            if tag == 'PERSON':
                if current_pers != "":
                    current_pers += " "
                current_pers += text
            else:
                if current_pers != "":
                    people.append(current_pers)
                    current_pers = ""

        if current_pers != "":
            people.append(current_pers)

        return people


class stanford_ORG(g.PropertyCoder):
    def run(self):
        tags = self['stanford_fullBody_3']

        organizations = []

        # merge consecutive
        current_org = ""
        for text, tag in tags:
            if tag == 'ORGANIZATION':
                if current_org != "":
                    current_org += " "
                current_org += text
            else:
                if current_org != "":
                    organizations.append(current_org)
                    current_org = ""

        if current_org != "":
            organizations.append(current_org)

        return organizations

class stanford_PERSON_title(g.PropertyCoder):
    from nlp import nerConnection

    loaded = False

    def load(self):
        if self.loaded:
            return

        from os.path import join
        import env
        from nltk.tag import StanfordNERTagger

        self.st = StanfordNERTagger(
            join(env.homeDir, 'stanford-ner-2018-10-16/classifiers/english.all.3class.caseless.distsim.crf.ser.gz'),
            join(env.homeDir, 'stanford-ner-2018-10-16/stanford-ner.jar')
        )

        self.loaded = True

    def run(self):
        self.load()

        from nltk import word_tokenize
        tags = self.st.tag(word_tokenize( self['title'].upper() ))

        people = []

        # merge consecutive
        current_pers = ""
        for text,tag in tags:
            if tag == 'PERSON':
                if current_pers != "":
                    current_pers += " "
                current_pers += text
            else:
                if current_pers != "":
                    people.append(current_pers)
                    current_pers = ""

        if current_pers != "":
            people.append(current_pers)

        return people