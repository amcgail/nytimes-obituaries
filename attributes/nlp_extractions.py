import g

class appos_words(g.PropertyCoder):

    def run(self):
        import nlp

        if self['spacyName'] is None:
            return []

        # Alec McGail, scientist and genius, died today.
        nameChildren = list(self["spacyName"].root.children)
        apposHooks = list(filter(lambda nameChild: nameChild.dep_ == 'appos', nameChildren))

        baseNouns = nlp.followRecursive(apposHooks, 'conj')
        return list(map(str, baseNouns))