import nltk
import occ
import re

coding_in = "v2.0"
n = 500

coder = occ.Coder()
coder.loadPreviouslyCoded(coding_in, rand=False, N=n)

for obit in coder.obituaries:
    sents = nltk.sent_tokenize(obit['fullBody'])
    died_sents = [i for i in range(len(sents)) if "died" in nltk.word_tokenize(sents[i])]

    if len(died_sents) == 0:
        print("Not even one died sentence!")
        continue

    # just choose the first one. it's going to be what we want I think
    died_sent_i = died_sents[0]
    died_sent = sents[died_sent_i]
    next_sent = sents[died_sent_i+1]

    after_died = died_sent[ re.search("\s+died\s+", died_sent).end(): ]

    # get rid of "today" and "yesterday"
    today = "today" in after_died
    yesterday = "yesterday" in after_died

    after_died.replace("today", "")
    after_died.replace("yesterday", "")

    # these are the dominant prepositions. find them and split by them
    preps = "in|of|at|near|on".split("|")
    parts = re.split("(\s+(?:%s)\s+)" % "|".join(preps), after_died)

    # now create yourself a good dictionary!
    info_dict = {}
    for i,v in enumerate(parts):
        if v.strip() in preps:
            info_dict[v.strip()] = parts[i+1]

    # on can be a date, or a day of the week

    # in can be a city
    if "in" in info_dict:
        location = geolocator.geocode(info_dict["in"])


    # at is usually a hospital, but also "his home"

    # of is what they died of

    # sometimes on and of are annoying: {'of': 'Spetsai', 'on': 'the Greek island', 'in': 'a clinic'}

    # the "next_sent" is now typically of the form: He was 67 years old. or has "lived in ___" "resident of ___" etc.

    print(info_dict, next_sent)