#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 12:51:31 2018

@author: alec
"""
import re

import wikipedia
from SPARQLWrapper import SPARQLWrapper, JSON
from dateutil import parser
from wikipedia import PageError, DisambiguationError

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

search_url = "https://www.wikidata.org/w/api.php?%s"

def subclassOf(what):
    # e.g. subclassOf("Q7210356") == political organization
    sparquery = """SELECT ?name
    WHERE
    {
         ?subClass wdt:P279 %s .
         ?theThing wdt:P31 ?subClass .
         ?theThing rdfs:label ?name .
         FILTER(LANG(?name) = "en")
    }
    """ % what

    sparql.setQuery(sparquery)
    r = sparql.query().convert()
    retNames = [x['name']['value'] for x in r['results']['bindings']]

    return retNames

def isXsubclassY(X, Y, params={}):
    # e.g. subclassOf("Q7210356") == political organization

    paramNames = " ".join( "?%s" % x for x in params.keys() )
    paramQueries = "\n".join( "?theThing %s %s ." %("wdt:%s"%val, "?%s"%key) for key,val in params.items() )

    sparquery = """SELECT ?name {paramNames}
    WHERE
    {{
         ?subClass (wdt:P279)* wd:{Y} .
         ?theThing wdt:{X} ?subClass .
         ?theThing rdfs:label ?name .
         {paramQueries}
         FILTER(LANG(?name) = "en")
    }}
    """.format(**locals())

    sparql.setQuery(sparquery)
    r = sparql.query().convert()
    retNames = [ {y: x[y]['value'] for y in x} for x in r['results']['bindings'] ]

    return retNames

def subclassOf(what):
    # e.g. subclassOf("Q7210356") == political organization
    sparquery = """SELECT ?name
    WHERE
    {
         ?subClass (wdt:P279)* %s .
         ?theThing wdt:P31 ?subClass .
         ?theThing rdfs:label ?name .
         FILTER(LANG(?name) = "en")
    }
    """ % what

    sparql.setQuery(sparquery)
    r = sparql.query().convert()
    retNames = [x['name']['value'] for x in r['results']['bindings']]

    return retNames

def companyNames():
    csparquery = """SELECT ?clab
    WHERE
    {
         ?company rdfs:label ?clab .
         ?company wdt:P31 ?cinstanceOf .
         ?cinstanceOf wdt:P279* wd:Q783794 .
         FILTER(LANG(?clab) = "en")
    }
    """
    
    sparql.setQuery(csparquery)
    r = sparql.query().convert()

    cnames = [ x['clab']['value'] for x in r['results']['bindings'] ]

    return cnames

if "famousDict" not in locals():
    famousDict = {}

def lookupOccupationalTitles(name):
    import urllib
    import json

    if name in famousDict:
        return famousDict[name]
    
    query = {
        "action":"wbsearchentities",
        "search": name,
        "language":"en",
        "format":"json"
    }

    sparquery = """SELECT ?occ
    WHERE
    {
    	%s wdt:P106 ?mainOcc .
         ?mainOcc (wdt:P279)* ?superOcc .
         ?superOcc rdfs:label ?occ .
         ?superOcc wdt:P31 wd:Q28640 .
         FILTER(LANG(?occ) = "en")
    }
    """

    with urllib.request.urlopen( search_url % urllib.parse.urlencode(query) ) as response:
        r = json.loads(response.read().decode('utf-8'))
        if r['success'] != 1 or len(r['search']) == 0:
            return []
        
        myid = r['search'][0]['id']
        sparql.setQuery(sparquery % "wd:%s" % myid)
        r2 = sparql.query().convert()
        
        occs = set( [ x['occ']['value'] for x in r2['results']['bindings'] ] )
        famousDict[name] = occs
        return list(occs)

def searchAndValidateWikipediaPage(search, obitDate):
    print("Starting the search for '%s'" % search)
    possible = list(wikipedia.search(search))
    print("Search for '%s' returned %s results. Taking max 3" % (search,len(possible)))
    for p in possible[:3]:
        valid, pid = validateWikipediaPage(p, obitDate)
        if valid:
            print("Valid match %s" % pid)
            return (valid, pid)

    return (False, None)

def validateWikipediaPage(name, obitDate, disambiguation_depth = 0):
    # prevents infinite loops (can't believe this happens!!)
    print("Processing name '%s'" % name)
    if disambiguation_depth > 1:
        #print("Avoided infinite loop...")
        return (False, None)

    try:
        if disambiguation_depth > 0:
            # this ensures we don't get a chain of disambiguations because of autocomplete!
            p = wikipedia.page(name, auto_suggest=False)
        else:
            p = wikipedia.page(name)
    except PageError:
        return (False, None)
    except DisambiguationError as e:
        # in the case of multiple articles, check each one
        print("Disambiguating %s options for %s" % (len(e.options), name))

        if len(e.options) > 10:
            print("Skipping ridiculous disambiguation")
            return (False, None)

        for option in e.options:
            valid, pid = validateWikipediaPage(option, obitDate, disambiguation_depth + 1)
            if not valid:
                continue
            return (valid, pid)

        # if none of the options are acceptable
        return (False, None)
    else:
        finalDeathDate = None

        # take the first three parens (sometimes there's extra junk)
        find_dates = re.findall("\(([^)]*)\)", p.content)[:3]

        # loop through and see if any are OK
        for find_date in find_dates:

            dateparts = re.split("[–-]", find_date)

            # this means the guy hasn't died yet!
            if len(dateparts) != 2:
                continue

            deathDate = dateparts[1]

            # this is to account for the pattern (Bronx, October 5, 1911 – Paris, July 14, 1989)
            deathDateParts = deathDate.split(",")
            if len(deathDateParts) > 2:
                # print("Redefining death date from %s to %s" % (deathDate, ",".join(deathDateParts[-2:])))
                deathDate = ",".join(deathDateParts[-2:])

            # if there's no date in here, neglect it
            if len(set("1234567890").intersection(deathDate)) == 0:
                continue

            # this is to account for the pattern June 19, 2012 in Pfafftown
            lastNumi = max(i for i in range(len(deathDate)) if deathDate[i] in "0123456789")
            # print("Redefining death date from %s to %s" % (deathDate, deathDate[:lastNumi+1]))
            deathDate = deathDate[:lastNumi + 1]

            # unaccountedfor pattern!!! (May 30, 1932, Dublin, Ireland – November 20, 1999; New York City, United States)

            try:
                deathDate = parser.parse(deathDate.strip())
            except ValueError:
                continue

            # found one that's OK!
            finalDeathDate = deathDate

        # this algorithm should cover some of the strange cases (although not all)
        if finalDeathDate is None:
            for find_date in find_dates:

                months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
                find_them = set()
                for month in months:
                    find_them.update( [m.start() for m in re.finditer(month, find_date)] )

                if len(find_them) == 2:
                    date1start, date2start = sorted(find_them)
                    date1str = find_date[date1start:date2start]
                    date2str = find_date[date2start:]

                    try:
                        deathDate = parser.parse(date2str.strip())
                    except ValueError:
                        continue

                    # found one that's OK!
                    finalDeathDate = deathDate
                    break

        if finalDeathDate is None:
            return (False, None)

        if finalDeathDate > obitDate:
            return (False, None)

        if (obitDate - finalDeathDate).days > 60:
            return (False, None)

        return (True, p.pageid)