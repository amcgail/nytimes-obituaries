import occ
import xlrd
from os.path import join, dirname

handCodingFn = "/home/alec/projects/nytimes-obituaries/hand_coding_originals/hand coding ds as combined sample aug 24.xlsx.xlsx.xlsx"

workbook = xlrd.open_workbook(handCodingFn)
worksheet = workbook.sheet_by_index(0)

coding = "v2.1"
coder = occ.Coder()
coder.loadPreviouslyCoded(coding)#, N=1, rand=False)

obits_by_id = {
    x['id']: x
    for x in coder.obituaries
}

ids = []

#for i in range(1, 101):
for i in range(1, 1001):
    if i % 50 == 0:
        print("finished with ", i, "... getting tired")

    id = int(worksheet.cell(i, 9).value)
    occ = worksheet.cell(i, 2).value

    if False:
        try:
            if int(occ) != 1:
                continue
        except ValueError:
            continue

    ids.append((id,occ))

ids = sample(ids, 200)
ids = sorted(ids)


with open(join(dirname(__file__), "ceos.txt"), 'w') as outf:
    for id, occ in ids:

        for _ in range(1):
            outf.write("-----------------%s-----------------------\n" % str(id))
        outf.write("\n")

        obit = obits_by_id[id]

        b = obit['fullBody']
        b = "\n".join([ x.strip() for x in b.split("\n") ])
        outf.write(b)
        outf.write("\n\n")