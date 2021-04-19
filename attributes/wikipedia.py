import g

class wikiPageId(g.PropertyCoder):
    def run(self):
        import wiki

        if self['name'] is None:
            return None

        date = self['date']
        if self['date_of_death'] is not None:
            date = self['date_of_death']

        valid, pid = wiki.searchAndValidateWikipediaPage(self['name'], date)

        return pid

class wiki_pageO(g.PropertyHelper):
    def run(self):
        from wikipedia import page

        if self['wikiPageId'] is None:
            return None

        return page(pageid=self['wikiPageId'])

class wiki_content(g.PropertyCoder):
    def run(self):
        if self['wiki_pageO'] is None:
            return None

        o_ = self['wiki_pageO']
        if o_ is not None:
            return o_.content
        return None

class wiki_links(g.PropertyCoder):
    def run(self):
        if self['wiki_pageO'] is None:
            return None

        o_ = self['wiki_pageO']
        if o_ is not None:
            return o_.links
        return None

class wiki_categories(g.PropertyCoder):
    def run(self):
        if self['wiki_pageO'] is None:
            return None

        o_ = self['wiki_pageO']
        if o_ is not None:
            return o_.categories
        return None

class wiki_death_date(g.PropertyCoder):
    def run(self):
        if self['wiki_pageO'] is None:
            return None
        import re
        from dateutil import parser

        finalDeathDate = None

        # take the first three parens (sometimes there's extra junk)
        find_dates = re.findall("\(([^)]*)\)", self['wiki_content'])[:3]

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
                #print("Redefining death date from %s to %s" % (deathDate, ",".join(deathDateParts[-2:])))
                deathDate = ",".join(deathDateParts[-2:])

            # if there's no date in here, neglect it
            if len(set("1234567890").intersection(deathDate)) == 0:
                continue

            # this is to account for the pattern June 19, 2012 in Pfafftown
            lastNumi = max(i for i in range(len(deathDate)) if deathDate[i] in "0123456789")
            #print("Redefining death date from %s to %s" % (deathDate, deathDate[:lastNumi+1]))
            deathDate = deathDate[:lastNumi+1]

            # unaccountedfor pattern!!! (May 30, 1932, Dublin, Ireland – November 20, 1999; New York City, United States)

            try:
                deathDate = parser.parse(deathDate.strip())
            except ValueError:
                continue

            # found one that's OK!
            finalDeathDate = deathDate
            break

        return finalDeathDate