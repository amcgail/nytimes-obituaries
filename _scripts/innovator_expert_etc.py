# * of *

import occ

coding = "v2.0"

coder = occ.Coder()
coder.loadPreviouslyCoded(coding)#, N=1, rand=False)

import re

for x in coder.obituaries:
    roles = ["innovator", "expert"]
    filler = ["in", "on", "of"]
    exp = "(?:%s) (%s) (.{0,50})" % ( "|".join(roles), "|".join(filler) )

    find_them = re.findall(exp, x['fullBody'])

    for y in find_them:
        print(y)