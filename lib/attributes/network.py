import g

class namesInObit(g.PropertyCoder):
    def run(self):
        from nlp import isPossibleFullName

        fb = self.ofWhat['spacyFullBody']
        possible_names = [str(x) for x in fb.ents if x.label_ == 'PERSON']
        names = list(filter(isPossibleFullName, possible_names))

        #print(str(fb))
        #print(names)
        return names

class namesInObitInWiki(g.PropertyCoder):
    def run(self):
        return None