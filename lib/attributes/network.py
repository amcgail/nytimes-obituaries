import g

class namesInObit(g.PropertyCoder):
    """
    Returns all the fully qualified names.

    There are still some issues with this attribute:
    + it can return places (Iwo Jima)
    + it takes a REALLY long time to compute
    """

    def run(self):
        from nlp import isPossibleFullName

        fb = self.ofWhat['spacyFullBody']
        possible_names = [str(x) for x in fb.ents if x.label_ == 'PERSON']
        names = list(filter(isPossibleFullName, possible_names))

        #print(str(fb))
        #print(names)
        return names

class namesInObitInWiki(g.OldPropertyCoder):
    def run(self):
        return None