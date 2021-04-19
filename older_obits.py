import glob
import re
import time
from collections import Counter, defaultdict
from itertools import chain
from os import path
from os.path import join, getmtime, getctime, exists

from dateutil import parser as dparse

from bs4 import UnicodeDammit

from datetime import datetime

import env

folder_names = {
    "SP2018": join( env.homeDir, "Dropbox/NYT Obituary Project, Independent Study" ),
    "FA2018": join( env.homeDir, "Dropbox/obituaries independent study, F 2018" ),
    "FA2019": join( env.homeDir, "Dropbox/obituaries independent study, F 2019" ),
    "SP2019": join( env.homeDir, "Dropbox/obituaries independent study, S 2019" )
}

class codingAnalysis:

    def fileInfo(self, obitf):
        result = {
            "has_attributes": False,
            "attributes": defaultdict(set)
        }

        raw = open(obitf, 'rb').read()
        raw = UnicodeDammit(raw).unicode_markup

        mtime = datetime.fromtimestamp(getmtime(obitf))
        ctime = datetime.fromtimestamp(getctime(obitf))

        result['mtime'] = mtime
        result['ctime'] = ctime
        result['fname'] = obitf

        lines = re.split("[\n\r]+", raw)

        line_matches = [re.match("^([A-Za-z ]{3,15}):(.*)", line) for line in lines]
        ix_match = [i for i in range(len(line_matches)) if line_matches[i] is not None]

        if not len(ix_match):
            pass
        else:
            last_match = max(ix_match)

            for m in line_matches:
                if m is None:
                    continue

                name = m.group(1).strip().upper()

                content = m.group(2).strip()

                if content == '':
                    continue
                
                result['has_attributes'] = True    
                result['attributes'][name].add(content)

            body = "\n".join(lines[last_match + 1:]).strip()
            result['nwords'] = len( body.split() )

            if self.keepInfo:
                result['body'] = body

        return result


    def __init__(self, collection_name=None, keepInfo=False, fgrep="*.txt"):

        print("Processing...")

        self.keepInfo = keepInfo
        self.attributeCounter = Counter()
        self.personCounter = Counter()
        self.personAttributeCounter = defaultdict(Counter)
        self.wordCountByPerson = defaultdict(list)
        self.hasAttributesByPerson = defaultdict(Counter)
        self.personYearCounter = defaultdict(Counter)
        self.attributeValues = defaultdict(set)
        self.infos = []

        if collection_name in folder_names:
            fn = folder_names[collection_name]
        else:
            if exists(collection_name):
                fn = collection_name
            else:
                raise Exception("Coding analysis must be run on one of: " + ",".join(folder_names.keys()), " OR a valid folder name")

        all_files = set(chain(
            glob.iglob( path.join( fn, "**", fgrep ), recursive=True ),
            glob.iglob(path.join(fn, fgrep), recursive=True),
        ))

        print("Directory", path.join( fn, "**", "*.txt" ))
        print(len(all_files), " files found")

        for f in all_files:

            name = None
            date_s = "Jan 1 1970"

            if collection_name in folder_names:
                parts = f.split(fn)[1]
                parts = parts.split(path.sep)

                if len(parts) < 4:
                    continue

                name = parts[1]

                if False:
                    print(parts)

                if collection_name == "FA2018":
                    if name in ["marwan"]:
                        date_s = "%s %s" % tuple(parts[2:4])
                    elif name in ['lily', "kendra", "beth", "sofia"]:
                        date_s = parts[3]
                    else:
                        continue

                elif collection_name == "SP2019":
                    if name in ["julia", "kendra", "sofia", "marwan", "jonathan", "katherine", "christian", "elizabeth"]:
                        date_s = "%s %s" % tuple(parts[2:4])
                    else:
                        continue

                elif collection_name == "SP2018":
                    if name in ["Michelle"]:
                        date_s = parts[2]
                    elif name in ["Emma","Samantha","Javier"]:
                        if parts[2] == "Notes:Borderline Cases":
                            continue
                        date_s = parts[3]
                    else:
                        continue

                elif collection_name == "FA2019":
                    if name in ['elizabeth','emma','lia','maria']:
                        date_s = " ".join( parts[2:4] )
                    elif name in ['helen']:
                        if len(parts) < 5:
                            continue
                        date_s = " ".join( [parts[2], parts[4]] )
                    else:
                        continue
                else:
                    continue

            # file modification date!!
            # TODO

            try:
                date = dparse.parse( date_s )
            except:
                continue

            info = self.fileInfo(f)
            self.hasAttributesByPerson[name].update([info['has_attributes']])

            # if no attributes, skip
            if not info['has_attributes']:
                continue

            # if no NAME, skip
            if 'NAME' not in info['attributes']:
                print(info['attributes'])
                continue

            self.attributeCounter.update( info['attributes'].keys() )
            for k in info['attributes']:
                self.attributeValues[k].update(info['attributes'][k])

            self.personCounter.update( [name] )
            self.wordCountByPerson[ name ].append( info['nwords'] )
            self.personAttributeCounter[name].update( info['attributes'].keys() )
            self.personYearCounter[name].update( [date.year] )

            if self.keepInfo:
                info['date'] = date
                info['name'] = name
                self.infos.append(info)

        print("Finished importing")
