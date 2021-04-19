import numpy as np
import glob
from os import path
from dateutil import parser as dparse
import re
from collections import Counter
from nltk.metrics import edit_distance
from bs4 import UnicodeDammit


obituaries = []
skipdollar = 0


attributeCounter = Counter()
personCounter = Counter()
knownAttributes = [('TITLE', 2168), ('DATE', 2167), ('SOURCE', 1207), ('SUBTITLE', 761), ('PHOTO', 50), ('LOCATION', 42)]
knownAttributes = [x[0] for x in knownAttributes] + ["ISSN"]

def add_obit( person, date, obitf ):
    global attributeCounter, personCounter
    global skipdollar

    raw = open(obitf, 'rb').read()
    raw = UnicodeDammit(raw).unicode_markup
    if False:
        try:
            raw = raw.decode("UTF8")
        except UnicodeDecodeError:
            try:
                raw = raw.decode("ISO-8859-1")
            except UnicodeDecodeError:
                try:
                    raw = raw.decode("UTF16")
                except:
                    print("SKIPPING -- UnicodeDecodeError", obitf)
                    raise

    date = dparse.parse(date)

    lines = re.split("[\n\r]*", raw)

    line_matches = [ re.match("^([A-Za-z]{3,8}):(.*)", line) for line in lines ]
    ix_match = [i for i in range(len(line_matches)) if line_matches[i] is not None]

    if not len(ix_match):
        print("SKIPPING -- contains no attributes", obitf)
        print(raw)
        return

    if set(raw).intersection( set("¢§") ):
        print("SKIPPING... Contains dollar characters", obitf)
        skipdollar += 1
        return

    last_match = max( ix_match )

    """
    # an important check:
    # this determines that there's no content __between lines__
    for i1, i2 in zip(ix_match, ix_match[1:] + [None]):
        name = line_matches[i1].group(1)
        content = line_matches[i1].group(2)
        if i2 is not None:
            content += "\n".join(lines[i1+1:i2])

            xtra = "\n".join(lines[i1+1:i2]).strip()
            if xtra != "":
                print("FOUNDFOUND")
                print(xtra)
                break

        print( name, content )
    """

    res = {}

    for m in line_matches:
        if m is None:
            continue

        name = m.group(1).strip().upper()

        attributeCounter.update([name])

        if name not in knownAttributes:
            min_d_i = min( range(len(knownAttributes)), key=lambda i: edit_distance(knownAttributes[i], name) )
            print("SWITCHING", knownAttributes[ min_d_i ], name)
            name = knownAttributes[ min_d_i ]

        content = m.group(2).strip()

        if name == 'SUBTITLE':
            if name not in res:
                res[name] = []
            res[name].append(content)
        elif name=='ISSN':
            pass
        else:
            res[name] = content

    body = "\n".join(lines[last_match + 1:]).strip()

    if len(body.split())<15:
        print("SHORT", obitf)
        print(line_matches)
        print(raw)

    res['body'] = body
    res['date'] = date
    res['fn'] = obitf
    res['person'] = person

    person = path.basename(person)
    personCounter.update([person])

    obituaries.append(res)



dataDir = path.join( path.dirname(__file__), "..", "data" )
people = glob.glob( path.join( dataDir, "FA 2018", "*" ) )

for personf in people:

    if "kendra" in personf:
        for dayf in glob.glob(path.join(personf, "*")):
            for datef in glob.glob(path.join(dayf, "*")):
                for obitf in glob.glob(path.join(datef, "TXT", "*.txt")):
                    person = path.basename(personf)
                    date = path.basename(datef)
                    add_obit(person, date, obitf)

    elif "beth" in personf:
        for dayf in glob.glob(path.join(personf, "*")):
            for datef in glob.glob(path.join(dayf, "*")):
                for obitf in glob.glob(path.join(datef, "clean text files", "*.txt")):
                    person = path.basename(personf)
                    date = path.basename(datef)
                    add_obit(person, date, obitf)

    else:
        for dayf in glob.glob(path.join(personf, "*")):
            for datef in glob.glob(path.join(dayf, "*")):
                for obitf in glob.glob(path.join(datef, "*.txt")):

                    person = path.basename(personf)
                    date = path.basename(datef)
                    add_obit(person, date, obitf)

# print(attributeCounter.most_common(10))


print(len(obituaries))
wcs = [ len(x['body'].split()) for x in obituaries ]
print(np.histogram(wcs, bins=5, range=(0,250)))

print( len([x for x in wcs if x > 250]) )

print( Counter([x['date'].year for x in obituaries]) )

print( sorted(wcs)[:10] )
print( sorted(wcs, reverse=True)[:10] )

#longest_ids = sorted(range(len(wcs)), key=lambda x: wcs[x], reverse=True)[:10]
#print(longest_ids)
# print( obituaries[longest_ids[1]]['body'], obituaries[longest_ids[2]]['body'] )
# print( wcs[longest_ids[1]], wcs[longest_ids[2]] )
# print( obituaries[longest_ids[1]]['fn'], obituaries[longest_ids[2]]['fn'] )

pyc_gt100 = Counter([ (x['person'], x['date'].year ) for x in obituaries if len(x['body'].split()) > 100 ])
pyc_all = Counter([ (x['person'], x['date'].year ) for x in obituaries ])

for x in sorted(pyc_gt100):
    print(x, ":", pyc_gt100[x])

for x in sorted(pyc_all):
    print(x, ":", pyc_all[x])

print("skipdollar", skipdollar)
print(personCounter)
print(attributeCounter)