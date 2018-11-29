import wiki

businessEntity = "Q1269299"
companyName = "The Co-operative Group"

q = """SELECT ?alsoKnownAs
WHERE
{{
    ?instance_of (wdt:P279)* wd:{businessEntity} .
    ?company wdt:P31 ?instance_of .
    ?company rdfs:label "{companyName}" .
    ?company rdfs:aliases ?alsoKnownAs .
    FILTER(LANG(?alsoKnownAs) = "en")
}}
""".format(**locals())

print(q)

wiki.sparql.setQuery(q)
r = wiki.sparql.query().convert()

import json
print(r)
print("\n".join( x['alsoKnownAs']['name'] for x in r['results']['bindings'] ))