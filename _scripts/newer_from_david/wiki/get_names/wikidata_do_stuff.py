import csv
import sys
sys.path.append('../../lib')

import wiki

dod = "P570"
gov = "Q889821"
subc = "P279"

q = """SELECT ?name ?dod ?gname
WHERE
{{
 ?guy wdt:P39 ?govt .
 ?govt (wdt:{subc})* wd:{gov} .
 ?guy wdt:{dod} ?dod .

 ?govt rdfs:label ?gname .
 FILTER(LANG(?gname) = "en") .

 ?guy rdfs:label ?name .
 FILTER(LANG(?name) = "en")
}}
""".format(**locals())

wiki.sparql.setQuery(q)
r = wiki.sparql.query().convert()

with open("wiki_govs.csv", 'w') as wikig:
	writer = csv.writer(wikig)
	writer.writerow(["name","dod","gov_of"])
	for x in r['results']['bindings']:
		row = [ x['name']['value'], x['dod']['value'], x['gname']['value'] ]
		writer.writerow(row)
