import xlrd
from random import sample
import occ
from xlutils.copy import copy
from nltk import jaccard_distance

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.0_extract")

infn = "/home/alec/projects/nytimes-obituaries/hand_coding_originals/hand coding ds as combined sample aug 24.xlsx.xlsx"

workbook = xlrd.open_workbook(infn)
worksheet = workbook.sheet_by_index(0)

workbook_c = copy(workbook)
worksheet_c = workbook_c.get_sheet(0)

c = {
    "title": 6,
    'newId': 9,
    'fullBody': 8
}

# do this once
# splits the body into words, and creates a set from that
tosearch = [
    (obit, set(obit['fullBody'].split()))
    for obit in coder.obituaries
]

#
#tosearch = [
#    (obit, set(sample(obit['fullBody'].split(), min(100, len(obit['fullBody'].split())))))
#    for obit in coder.obituaries
#]
#

for i in range(1, 1001):
    if i % 5 == 0:
        print(i)

    t = worksheet.cell(i, c['title']).value
    fb = worksheet.cell(i, c['fullBody']).value

    if not(type(t) != str) and not(len(t) < 5):
        continue

    #if not(len(t) < 5):
    #    continue

    mywords = set(fb.split())
    mywordl = len(mywords)

    ds = [ (
        obit,
        len(mywords.intersection(words)) / mywordl
    ) for obit,words in tosearch ]

    matches = [x for x in ds if x[1] > 0.9]

    if len(matches) < 1:
        print( fb )
        print(t)
        print(len([x for x in ds if x[1] > 0.9]), len([x for x in ds if x[1] > 0.8]), len([x for x in ds if x[1] > 0.6]))
        raise Exception("WAHH")

    if len(matches) > 1:
        for obit, _ in matches[1:]:
            obit.destroy()

    match = matches[0]
    id = match[0]['id']
    worksheet_c.write(i, c['newId'], id)

    continue

    ids = [
        x['id']
        for x in coder.obituaries
        if x['title'] in t or t in x['title']
           and len(x['title']) >= 5
    ]

    if False:
        # this is DEFINITELY creating more problems than it's dealing with :(
        fbchunks = [ fb[sindex:sindex+50] for sindex in range(0,500,50) ]
        fbchunks = [ x for x in fbchunks ]
        ids += [
            x['id']
            for x in coder.obituaries
            if any(fbchunk in x['fullBody'] for fbchunk in fbchunks)
        ]

    ids = list(set(ids))

    if len(ids) == 0:
        print(fbchunk)
        print(fb)
        print(t)
        raise Exception("NOOOO!")

    if len(ids) > 1:
        for id in ids[1:]:
            coder.findObitByInfo(id=id).destroy()

    id = ids[0]

    worksheet_c.write(i, c['newId'], id)

workbook_c.save(infn + ".xlsx")