from os import path

import occ

from wiki import validateWikipediaPage

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1", rand=False, attrs=["name","firstSentence","date","id","wikiPageId"])

for obit in coder.obituaries:
    #if obit['name'] not in ['Jim Drake','Omar Torrijos Herrera']:
    if "wikiPageId" in obit._prop_cache:
        print("Already done: ", obit['name'])
        continue

    print("Doing: ", obit['name'])

    n = obit['name']
    d = obit['date']

    valid, pid = validateWikipediaPage(n, d)

    print("Trying... ", n, d)

    if not valid:
        print("NOT FOUND: ", pid)
    else:
        print("FOUND: ", n, " -- ", pid)

    # load the whole thing, so I can add this attribute
    obitSave = occ.obitFromId("v2.1", obit['id'])
    obitSave['wikiPageId'] = pid
    with open( path.join( "/home/alec/codeDumps/v2.1/%s.pickle" % obitSave['id'] ), 'wb' ) as of:
        of.write(obitSave.to_pickle())