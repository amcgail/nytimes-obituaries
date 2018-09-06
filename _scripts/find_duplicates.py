import occ

from operator import itemgetter
from itertools import groupby

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.0_extract", rand=False)

if False:
    for _, v in groupby(sorted(coder.obituaries, key=itemgetter("fullBody")), itemgetter("fullBody")):
        v = list(v)
        if len(v) <= 1:
            continue

        print({x['id'] for x in v})

        for doc in v[1:]:
            print("destroying '%s'" % doc['id'])
            doc.destroy()

"""
{4457, 4453}
destroying '4457'
{42304, 3384}
destroying '3384'
{28424, 50596}
destroying '28424'
{58051, 58055}
destroying '58055'
{58026, 58027}
destroying '58027'
{5570, 5573}
destroying '5570'
{10113, 10114}
destroying '10113'
{51136, 51129}
destroying '51136'
{29555, 29564}
destroying '29564'
{52554, 52558}
destroying '52554'
{33864, 33857}
destroying '33857'
{35952, 35954}
destroying '35954'
{16961, 16949}
destroying '16961'
{15872, 15877}
destroying '15877'
{313, 311}
destroying '313'
{55089, 55086}
destroying '55086'
{46862, 46871}
destroying '46871'
{22970, 22995}
destroying '22995'
{18730, 18731}
destroying '18730'
{43490, 43491}
destroying '43490'
{55626, 55619}
destroying '55626'
{29720, 29691}
destroying '29691'
{4833, 30}
destroying '30'
{40057, 40085}
destroying '40085'
{10434, 10428}
destroying '10428'
{7704, 7707}
destroying '7707'
{7408, 7403}
destroying '7403'
{7634, 7646}
destroying '7634'
{8247, 8239}
destroying '8247'
{26363, 26382}
destroying '26382'
{47994, 47980}
destroying '47980'
{5176, 5167}
destroying '5167'
{4192, 4189}
destroying '4192'
{54348, 33293}
destroying '33293'
{58185, 58178}
destroying '58185'
{55417, 55426}
destroying '55417'
{28, 4831}
destroying '4831'
{16152, 16157}
destroying '16157'
{17936, 17943}
destroying '17943'
{25870, 25863}
destroying '25870'
{8072, 8071}
destroying '8072'
{24312, 24303}
destroying '24303'
{54347, 33292}
destroying '33292'
{23948, 23956}
destroying '23948'
{4832, 29}
destroying '29'
{1962, 1958}
destroying '1958'
{33749, 33742}
destroying '33749'
{10405, 10429}
destroying '10429'
{40160, 40163}
destroying '40160'
{8224, 8235}
destroying '8224'
{50705, 50703}
destroying '50703'
{24202, 24196}
destroying '24202'
{46880, 46868}
destroying '46880'
{11377, 11379}
destroying '11379'
{35833, 35834}
destroying '35834'
{41344, 41356}
destroying '41356'
{42184, 42196}
destroying '42196'
{16947, 16950}
destroying '16950'
{46612, 46605}
destroying '46612'
{53552, 53548}
destroying '53548'
{55532, 55540}
destroying '55532'
{38473, 38468}
destroying '38468'
{45045, 45054}
destroying '45045'
{23275, 23270}
destroying '23270'
{13422, 13430}
destroying '13422'
{18077, 18062}
destroying '18077'
{17884, 17893}
destroying '17893'
{39218, 39226}
destroying '39226'
{24168, 24178}
destroying '24178'
{42300, 3382}
destroying '3382'
{55427, 55415}
destroying '55415'
{48897, 48890}
destroying '48897'
{33289, 54340}
destroying '33289'
{27921, 27914}
destroying '27914'
{752, 755}
destroying '752'
{40114, 40108}
destroying '40114'
{50594, 28422}
destroying '50594'
{11957, 11959}
destroying '11959'
{60869, 60871}
destroying '60871'
{47690, 47691}
destroying '47690'
{40162, 40159}
destroying '40162'
{40115, 40110}
destroying '40115'
{36424, 36423}
destroying '36424'
{11602, 11589}
destroying '11589'
{15688, 15684}
destroying '15684'
{41204, 46895}
destroying '41204'
{26208, 26219}
destroying '26208'
{41338, 41354}
destroying '41354'
{4240, 4245}
destroying '4245'
{60504, 60494}
destroying '60494'
{44528, 44523}
destroying '44523'
{58345, 54668}
destroying '58345'
{39005, 39015}
destroying '39015'
{23065, 23053}
destroying '23053'
{45882, 21204}
destroying '21204'
{26336, 26341}
destroying '26336'
{11643, 11637}
destroying '11637'
{23248, 23244}
destroying '23244'
{23881, 23876}
destroying '23876'
{26256, 26252}
destroying '26256'
{47810, 47803}
destroying '47803'
{51553, 51549}
destroying '51549'
{40112, 40117}
destroying '40112'
{7497, 7494}
destroying '7494'
{20904, 20893}
destroying '20893'
{54656, 31078}
destroying '54656'
{10131, 10101}
destroying '10131'
{26435, 54940}
destroying '54940'
{10380, 10382}
destroying '10380'
{60246, 60231}
destroying '60246'
{16835, 16829}
destroying '16835'
{10448, 10441}
destroying '10448'
{10120, 10107}
destroying '10107'
{28154, 28151}
destroying '28154'
{15378, 15381}
destroying '15378'
{33290, 54339}
destroying '54339'
{10147, 10155}
destroying '10155'
{41988, 41982}
destroying '41988'
{48681, 48695}
destroying '48695'
{16200, 16196}
destroying '16196'
{15981, 15975}
destroying '15975'
{7897, 7894}
destroying '7894'
{29673, 29675}
destroying '29673'
"""


# ANOTHER WAY :(
todelete = []
for i,doc in enumerate(coder.obituaries):
    if i % 1000 == 0:
        print("Finished ",i," obituaries!")

    fb = doc['fullBody']
    fbchunk = fb[15:115]

    if len(fbchunk) <= 20:
        print("Too short: %s" % doc['id'])

    matches = [ d for d in coder.obituaries if d not in todelete and fbchunk in d['fullBody'] ]

    if len(matches) > 1:
        print("Duplicate found!")
        for d in matches[1:]:
            todelete.append(d)
            print("---" + d['title'])

for x in todelete:
    assert(isinstance(x, occ.Doc))
    x.destroy()