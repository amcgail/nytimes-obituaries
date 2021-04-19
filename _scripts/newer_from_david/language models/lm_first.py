from nlp import NgramModel
import occ

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1")
docs = [x['fullBody'] for x in coder.obituaries]
del coder

ngm = NgramModel(3, docs)