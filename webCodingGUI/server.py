import sys
from os import path

from flask import Flask, request, send_from_directory
from pymongo import MongoClient
from random import sample
import json, re

from os import path
import sys
from collections import Counter

basedir = path.join(path.dirname(__file__), "..")
sys.path.append(path.join(basedir, 'lib'))
import occ, wikidata, g, nlp

app = Flask(__name__, static_url_path='/static')

db = MongoClient()['occCodingNotes']

mycoder = occ.Coder()
mycoder.loadCodes(path.join("..", "codeDumps", "coding5000"))


@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route('/js/<path:path>')
def send_js(jsf):
    return send_from_directory('static/js', jsf)


@app.route('/addNote', methods=['POST'])
def addNote():
    fn = request.form["fn"]
    note = request.form["note"]

    db['freeFormNotes'].insert({"fn": fn, "note": note, "time": datetime.now()})
    return "1"


@app.route('/addVocab', methods=['POST'])
def addVocab():
    from datetime import datetime
    code = request.form["code"]
    word = request.form["word"]

    db['newWords'].insert({"code": code, "word": word, "time": datetime.now()})
    return "1"


@app.route('/delVocab', methods=['POST'])
def delVocab():
    from datetime import datetime
    code = request.form["code"]
    word = request.form["word"]

    db['badWords'].insert({"code": code, "word": word, "time": datetime.now()})
    return "1"


@app.route('/seeAllComments')
def nowhere():
    return "under construction"


@app.route('/correctCoding', methods=['POST'])
def correctCoding():
    from datetime import datetime
    fn = request.form["fn"]
    code = request.form["code"]

    db['correctCoding'].insert({"code": code, "fn": fn, "time": datetime.now()})
    return "1"


@app.route('/getRandom/<int:num>')
def getRandom(num):
    docs = sample( mycoder.docs, num )

    ret = []

    for d in docs:
        assert(isinstance(d, occ.Doc))
        if d['fName'] not in fidToCode:
            continue

        fn = d.info['fName']
        topCodes = d.guess
        body = d.info["fullBody"]

        colors = [
            "#9B59B6",
            "#45B39D",
            "#F5B041",
            "#4A235A",
            "#34495E",
            "#FF00FF"
        ]

        codes = mycoder.extractCodesDetailed(body)

        """
        codeC = [ x['code'] for x in codes ]

        for c in topCodes:
            if c in codeC:
                codeC.remove(c)

        codeC = Counter(codeC)
        codeC = codeC.items()
        codeC = sorted(codeC, key=lambda x: x[1], reverse=True)[:len(colors)]

        codesToKeep = [ x[0] for x in codeC ]
        """

        codeMap = {
            topCodes.keys()[i]: colors[i]
            for i in range(len(topCodes))
        }

        sent = nlp.sent_tokenize(body)
        body = ""
        expandContract = False

        for i in range(0, len(sent), 5):
            if i == 5 * 2:
                expandContract = True
                body += "<button class='expandBtn'>More/Less</button>"
                body += "<div class='expandDiv'>"

            body += "<p>"
            body += "\n".join(sent[i:i + 5])
            body += "</p>"

        if expandContract:
            body += "</div>"

        def c2n(c):
            codeName = "--"
            if c in occ.codeToName:
                codeName = occ.codeToName[c]
            return codeName

        for c in codes:  # sorted( codes, key=lambda x: len(x['word']), reverse=True ):
            if c['code'] not in topCodes:
                continue

            body = re.sub(
                r"\b%s\b" % c['word'],
                "<span title='%s (%s)' style='color:%s; font-weight:bold'>%s</span>" %
                (c['code'], c2n(c['code']), codeMap[c['code']], c['word']),
                body
            )

        lCont = [
            "<span style='color:%s; font-weight:bold'>%s (%s): %0.03f</span><br>" % (
            col, code, c2n(code), float(topCodes[code]))
            for (code, col) in codeMap.items()
        ]
        lCont = "".join(lCont)

        legend = "<div class='legend'>%s</div>" % lCont

        ret.append({
            "fn": fn,
            "date": d.info["date"],
            "title": d.info["title"],
            "body": "<h2>%s (%s)</h2>" % (d.info["title"], d.info["fName"]) + legend + body,
            "codes": codes,
            "codeMap": codeMap
        })

    return json.dumps(ret)


app.debug = True
app.run(port=5000)
