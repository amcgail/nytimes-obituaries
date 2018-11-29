import g

# the following two are no longer used
class title(g.PropertyCoder):

    def run(self):
        import re

        title_parts = re.split("[\r\n]+", self.ofWhat['_title'])
        # print(title_parts)
        last_line = "\n".join(title_parts[-1:])
        return last_line.strip()


class title_helper(g.PropertyHelper):

    def hasNumber(self, x):
        return any(y.strip().isnumeric() for y in x.split())

    def extractNumber(self, x):
        for y in x.split():
            ys = y.strip()
            if ys.isnumeric():
                return int(ys)

        return None

    def parseCommas(self, s):
        ret = {}

        parts = s.split(",")

        if len(parts) == 1:
            ret['unparsed'] = parts[0]

        if len(parts) == 2:
            name, age = parts
            ret['name'] = name
            ret['age'] = self.extractNumber(age)

        elif len(parts) == 3:
            ret['name'] = parts[0]

            if self.hasNumber(parts[1]):
                ret['age'] = self.extractNumber(parts[1])
                ret['desc'] = parts[2]
            else:
                ret['age'] = self.extractNumber(parts[2])
                ret['desc'] = parts[1]
        elif len(parts) == 4:
            ret['name'] = parts[0]

            if self.hasNumber(parts[3]):
                ret['age'] = self.extractNumber(parts[3])

                ret['desc'] = parts[1]
                ret['desc2'] = parts[2]
            elif self.hasNumber(parts[1]):
                ret['age'] = self.extractNumber(parts[1])

                ret['desc'] = parts[2]
                ret['desc2'] = parts[3]
            elif self.hasNumber(parts[2]):
                ret['age'] = self.extractNumber(parts[2])

                ret['desc'] = parts[1]
                ret['desc2'] = parts[3]


        return ret

    def run(self):
        t = self.ofWhat['title']

        ret = {}

        if ";" in t:
            parts = t.split(";")
            if len(parts) == 2:
                name_age, subt = parts

                ret.update(self.parseCommas(name_age))
                ret['subt'] = subt
        else:
            ret.update(self.parseCommas(t))


        print(t)
        print(ret)

        return ret


class title_name(g.PropertyCoder):
    def run(self):
        from nlp import isPossibleFullName

        tp = self.ofWhat['title_parts']
        print(tp)
        tp = list( filter(isPossibleFullName, tp) )
        print(tp)
        return tp

