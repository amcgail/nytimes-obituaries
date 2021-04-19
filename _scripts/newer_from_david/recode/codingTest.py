import occ

occ.testAttributeCoding(
    loadDirName="v2.1",
    attrName="appos_words",
    toRecode=["spacyName"],
    N=50,
    debugAttrs=["name", "firstSentence"]
    #condition=lambda x: x['title_info']['name'] is not None and x['title_info']['name'].lower().split()[-1] != x['spacyName'].lower().split()[-1]
)

#
# occ.testAttributeCoding(
#     loadDirName="v2.1",
#     attrName="title_info",
#     N=50,
#     debugAttrs=["title"]
# )