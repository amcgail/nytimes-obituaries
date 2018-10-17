import wiki

ceo = "Q428322"
leader_of_org = "Q25713832"
pheld = "P39"
gmotors = "Q81965"

q = """SELECT ?name
WHERE
{{
    ?pheld (wdt:P279)* wd:{leader_of_org} .
    ?ceo wdt:{pheld} ?pheld .
    ?ceo wdt:P108 wd:{gmotors} .
    ?ceo rdfs:label ?name .
    FILTER(LANG(?name) = "en")
}}
""".format(**locals())

wiki.sparql.setQuery(q)
r = wiki.sparql.query().convert()

import json
print(r)
print("\n".join( x['name']['value'] for x in r['results']['bindings'] ))