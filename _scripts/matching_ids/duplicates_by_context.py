import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", rand=False)

ntodo = 1000
count = 0

for obit in coder.obituaries[:1000]:

    def closeEnough(x):
        if not x['name'] == obit['name']:
            return False
        if not abs( (obit['date'] - x['date']).days ) < 5:
            return False
        return True

    find = list(filter(closeEnough, coder.obituaries))

    if len(find) > 1:
        print("------------")
        for f in find:
            print(f['date'], f['name'], '::', f['title'])

        count += 1


print("%s out of %s were actually duplicates!" % (count, len(coder.obituaries)))