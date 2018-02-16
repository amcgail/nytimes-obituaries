from flask import Flask, request, send_from_directory, url_for
import json
import sys
from os import path
import json
from collections import Counter
import re

from pymongo import MongoClient

app = Flask(__name__, static_url_path='/static')

sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )
from lib import *

db = MongoClient()['occCodingNotes']

fidToCode = {}

thirdSFn = path.join( '..', 'coding', 'thirdStabCoding.csv' )
with open(thirdSFn) as thirdSF:
	for row in DictReader(thirdSF):
		fidToCode[ row['fn'] ] = {
			row["code1"]: row["confidence1"],
			row["code2"]: row["confidence2"],
			row["code3"]: row["confidence3"]
		}

codeToName = {}
officialTitlesFn = path.join( '..', 'coding', 'occ2000.officialTitles.csv' )
with open(officialTitlesFn) as officialTitlesF:
	for row in DictReader(officialTitlesF):
		if row['officialTitle'] == "":
			continue

		code = "occ2000-%03d" % int(row['code'])

		codeToName[ code ] = row['officialTitle']

#print codeToName.keys()

@app.route("/")
def index():
	return app.send_static_file('index.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/addNote', methods=['POST'])
def addNote():
	fn = request.form["fn"]
	note = request.form["note"]

	db['freeFormNotes'].insert({"fn":fn, "note":note, "time": datetime.now()})
	return "1"

@app.route('/addVocab', methods=['POST'])
def addVocab():
	from datetime import datetime
	code = request.form["code"]
	word = request.form["word"]

	db['newWords'].insert({"code":code, "word":word, "time": datetime.now()})
	return "1"

@app.route('/delVocab', methods=['POST'])
def delVocab():
	from datetime import datetime
	code = request.form["code"]
	word = request.form["word"]

	db['badWords'].insert({"code":code, "word":word, "time": datetime.now()})
	return "1"
 
@app.route('/seeAllComments')
def nowhere():
    return "under construction"
 
@app.route('/correctCoding', methods=['POST'])
def correctCoding():
	from datetime import datetime
	fn = request.form["fn"]
	code = request.form["code"]

	db['correctCoding'].insert({"code":code, "fn":fn, "time": datetime.now()})
	return "1"

@app.route('/getRandom/<int:num>')
def getRandom(num):
	docs = getRandomDocs(num)

	ret = []

	for d in docs:
		if d['fName'] not in fidToCode:
			continue

		fn = d["fName"]
		topCodes = fidToCode[fn]		
		body = d["fullBody"]

		colors = [
			"#9B59B6",
			"#45B39D",
			"#F5B041",
			"#4A235A",
			"#34495E",
			"#FF00FF"
		]

		codes = extractCodesDetailed(d["fullBody"])

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

		sent = sent_tokenize(body)
		body = ""
		expandContract = False

		for i in range(0, len(sent), 5):
			if i == 5*2:
				expandContract = True
				body += "<button class='expandBtn'>More/Less</button>"
				body += "<div class='expandDiv'>"

			body += "<p>"
			body += "\n".join( sent[i:i+5] )
			body += "</p>"

		if expandContract:
			body += "</div>"

		def c2n(c):
			codeName = "--"
			if c in codeToName:
				codeName = codeToName[c]
			return codeName

		for c in codes: #sorted( codes, key=lambda x: len(x['word']), reverse=True ):
			if c['code'] not in topCodes:
				continue

			body = re.sub( 
				r"\b%s\b" % c['word'], 
				"<span title='%s (%s)' style='color:%s; font-weight:bold'>%s</span>" % 
					(c['code'], c2n(c['code']), codeMap[ c['code'] ], c['word']),
				body
			)

		lCont = [
			"<span style='color:%s; font-weight:bold'>%s (%s): %0.03f</span><br>" % (col, code, c2n(code), float(topCodes[code]))
			for (code, col) in codeMap.items()
		]
		lCont = "".join(lCont)

		legend = "<div class='legend'>%s</div>" % lCont

		ret.append( {
			"fn": d["fName"],
			"date": d["date"],
			"title": d["title"],
			"body": "<h2>%s (%s)</h2>" % (d["title"], d["fName"]) + legend + body,
			"codes": codes,
			"codeMap": codeMap
		})

	return json.dumps(ret)
