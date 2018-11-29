"""
The idea here is to accept ALL terms as correct.
Then when a term is found, we can use the relations between the words their context to determine if they should be counted.
Could start by learning a simple linear model...

If we have a
"""

# Alec McGail, scientist and genius, died today.
nameChildren = list(self["spacyName"].root.children)
apposHooks = list(filter(lambda x: x.dep_ == 'appos', nameChildren))

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
        result = coding.nounOCC(n)

        coding.stateCounter.update([result['state']])
        coding.count(space=result['state'], key=result['word'])

        guesses.append(result)

self.guess = guesses

# Alec McGail, who ..., died today.
relcls = list(filter(lambda x: x.dep_ == 'relcl', nameChildren))
