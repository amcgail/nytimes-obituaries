import occ
import nlp

coder = occ.Coder()
coder.loadPreviouslyCoded("all_v2.0", N=None, rand=False)

def hasDeath(x):
    dd = ["died", "dead"]
    for d in dd:
        if d in x:
            return True
    return False

for x in coder.obituaries:
    ss = nlp.sent_tokenize(x['fullBody'])
    ss_d = [ x for x in ss if hasDeath(x) ]
    if len(ss_d) > 1:
        #print(ss_d)
        pass
    if len(ss_d) == 0:
        print("FAILED----------------------------------")
        print(ss)