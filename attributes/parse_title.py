import g

# the following two are no longer used
class title(g.PropertyCoder):

    def run(self):
        import re

        if '_title' in self.ofWhat:
            pre_title = self.ofWhat['_title']
        elif 'HAND_TITLE' in self.ofWhat:
            pre_title = self.ofWhat['HAND_TITLE']
        else:
            raise Exception("No title found")


        title_parts = re.split("[\r\n]+", pre_title)
        # print(title_parts)
        last_line = "\n".join(title_parts[-1:])
        return last_line.strip()


class title_info(g.PropertyCoder):
    """
    Extracts the information contained in the title, to the best of its ability.
    This does a pretty great job.

    It'll return a dictionary with default:
        {
            "name":None,
            "age":None,
            "desc":None,
            "desc2":None,
            "unparsed":None
        }
    """

    def hasNumber(self, x):
        return any(y.strip().isnumeric() for y in x.split())

    def extractNumber(self, x):
        for y in x.split():
            ys = y.strip()
            if ys.isnumeric():
                return int(ys)

        return None

    def parseCommas(self, s):
        import re
        ret = {}

        # notes:
        # a single "-" needs a space after it, so it's not confused with "Martinez-Gomez-Ramirez"
        parts = re.split("(?:,+|-{2,}|-\s|;+|dies at|is dead|dies|dead at|dead)", s, flags=re.IGNORECASE)
        parts = [x.strip() for x in parts]
        parts = [x for x in parts if x != ""]

        if len(parts) == 1:
            ret['unparsed'] = parts[0]

        if len(parts) == 2:
            name, age = parts
            ret['name'] = name
            if self.hasNumber(age):
                ret['age'] = self.extractNumber(age)
            else:
                ret['desc'] = age

        elif len(parts) == 3:
            ret['name'] = parts[0]

            if self.hasNumber(parts[1]):
                ret['age'] = self.extractNumber(parts[1])
                ret['desc'] = parts[2]
            elif self.hasNumber(parts[2]):
                ret['age'] = self.extractNumber(parts[2])
                ret['desc'] = parts[1]
            else:
                ret['desc'] = parts[1]
                ret['desc2'] = parts[2]
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

        # if the whole thing is uppercase, turn it into title case
        if t.upper() == t:
            t = t.title()

        ret = {
            "name":None,
            "age":None,
            "desc":None,
            "desc2":None,
            "unparsed":None
        }

        if False:
            if ";" in t:
                parts = t.split(";")
                if len(parts) == 2:
                    name_age, subt = parts

                    ret.update(self.parseCommas(name_age))
                    ret['subt'] = subt
            else:
                ret.update(self.parseCommas(t))

        ret.update(self.parseCommas(t))

        return ret