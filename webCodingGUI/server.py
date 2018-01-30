from flask import Flask, request, send_from_directory, url_for
import json
import sys
from os import path
import json
from collections import Counter
import re

app = Flask(__name__, static_url_path='/static')

sys.path.append( path.join( path.dirname(__file__), '..', 'lib' ) )
from lib import *

@app.route("/")
def index():
	return app.send_static_file('index.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/getRandom/<int:num>')
def getRandom(num):
	docs = getRandomDocs(num)

	ret = []

	for d in docs:
		codes = extractCodesDetailed(d[4])
		body = d[4]

		colors = [
			"#C0392B",
			"#9B59B6",
			"#45B39D",
			"#F5B041",
			"#4A235A",
			"#34495E",
			"#FF00FF"
		]

		codeC = Counter([ x['code'] for x in codes])
		codeC = codeC.items()
		codeC = sorted(codeC, key=lambda x: x[1], reverse=True)[:len(colors)]

		codesToKeep = [ x[0] for x in codeC ]
		print(codesToKeep)

		codeMap = {
			codesToKeep[i]: colors[i]
			for i in range(len(codesToKeep))
		}

		sent = sent_tokenize(body)
		body = ""
		for i in range(0, len(sent), 5):
			if i == 5*2:
				expandContract = True
				body += "<button class='expandBtn'>More/Less</button>"
				body += "<dib class='expandDiv'>"

			body += "<p>"
			body += "\n".join( sent[i:i+5] )
			body += "</p>"

		if expandContract:
			body += "</div>"

		for c in sorted( codes, key=lambda x: len(x['word']), reverse=True ):
			if c['code'] not in codesToKeep:
				continue

			body = re.sub( 
				r"\b%s\b" % c['word'], 
				"<span title='%s' style='color:%s; font-weight:bold'>%s</span>" % 
					(c['code'], codeMap[ c['code'] ], c['word']),
				body
			)

		lCont = [
			"<span style='color:%s; font-weight:bold'>%s</span><br>" % (col, code)
			for (code, col) in codeMap.items()
		]
		lCont = "".join(lCont)

		legend = "<div class='legend'>%s</div>" % lCont

		ret.append( {
			"fn": d[0],
			"date": d[1],
			"title": d[2],
			"body": legend + body,
			"codes": codes,
			"codeMap": codeMap
		})

	return json.dumps(ret)