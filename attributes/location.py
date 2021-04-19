import g, nlp
from ratelim import patient

from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="strangResearch")

geocode_cache = {}

def bbEitherContains(bb1, bb2):
    return any([
        bbContains(bb1, bb2),
        bbContains(bb2, bb1),
    ])


def bbContains(bb1, bb2):
    p1 = (x11, x12, y11, y12) = list(map(float,bb1))
    p2 = (x21, x22, y21, y22) = list(map(float, bb2))

    return all([
        x11 <= x21,
        y11 >= y21,
        x22 <= x12,
        y22 >= y12,
    ])

def geocode(locstr):
    locstr = locstr.strip(",")
    if locstr in geocode_cache:
        return geocode_cache[locstr]

    result = geocode_api(locstr)
    geocode_cache[locstr] = result
    return result

@patient(max_calls=10, time_interval=10)
def geocode_api(locstr):
    keys = "class,lat,lon,boundingbox,importance,place_id,display_name".split(",")
    #print(locstr)

    lookup = geolocator.geocode(locstr, exactly_one=False)

    if len(lookup):

        print(len(lookup))
        print(lookup)
        return

        if lookup.raw['class'] in ['amenity']:
            return None

        result = {
            k: lookup.raw[k] for k in keys
        }

        result['boundingbox'] = list(map(float,result['boundingbox']))
        (x1, x2, y1, y2) = bb = result['boundingbox']

        result['bbArea'] = (y2-y1)*(x2-x1)

        print(result)
        return result

    return None

class location_all(g.PropertyCoder):
    def run(self):
        from collections import OrderedDict
        place_strings = self['stanford_LOCATION']

        place_strings = list(OrderedDict.fromkeys(place_strings))

        places = []
        for p in place_strings:
            gc = geocode(p)
            if gc is None:
                continue

            places.append(gc)

        return places

class location_died(g.PropertyCoder):
    def run(self):
        from operator import itemgetter

        place_strings = self['stanford_LOCATION']

        died_sent = self['died_sentence']
        if died_sent is None:
            return None
        #print(died_sent)

        look_die = died_sent.find( "die" )

        place_distance_die = []
        for i, p in enumerate(place_strings):
            look_place = died_sent.find( p )
            if look_place == -1:
                place_distance_die.append( 1e9 )
                continue

            if look_place < look_die:
                place_distance_die.append(abs(look_place - look_die) + 1e4)
                continue

            place_distance_die.append( look_place - look_die )

        places = zip( place_strings, place_distance_die )
        places = sorted( places, key=itemgetter(1) )

        gcs = []

        for p, dist in places:
            if dist >= 1e4:
                continue

            if len(p) < 5:
                continue

            gc = geocode(p)
            if gc is None:
                continue

            gcs.append(gc)

        #print( [x['display_name'] for x in gcs] )

        if len(gcs):
            # this is just a first option... the most important
            # return sorted(gcs, key=itemgetter("importance"), reverse=True)[0]

            # second option: they must all be referring to the same place.
            # pairwise containment
            for i, x in enumerate(gcs):
                for j, y in enumerate(gcs):
                    if i >= j:
                        continue

                    if not bbEitherContains(x['boundingbox'], y['boundingbox']):
                        return None

            # return any of them.
            # this could be replaced with the most accurate.
            return gcs[0]
        else:
            return None

        return None