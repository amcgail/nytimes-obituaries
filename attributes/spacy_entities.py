import g

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