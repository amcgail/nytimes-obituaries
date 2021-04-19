sparquery = """SELECT ?
WHERE
{
	%s wdt:P106 ?mainOcc .
     ?mainOcc (wdt:P279)* ?superOcc .
     ?superOcc rdfs:label ?occ .
     ?superOcc wdt:P31 wd:Q28640 .
     FILTER(LANG(?occ) = "en")
}
"""
