import os
import sys
import time
import json
import argparse
import unidecode

import requests
from googlegeocoder import GoogleGeocoder
from slugify import slugify

MAIN = 'https://gw.cyclocity.fr/3311a6cea2e49b10/'

ACTIONS = {
    'cities': 'contracts/full?token={token}',
    'token': 'token/key/b885ab926fdca7dbfbf717084fb36b5f',
    'availability': 'availability/{city}/stations/state/?token={token}',
    'availabitity_by_geo': 'availability/{city}/stations/proximity/{what}?lat={lat}&lng={lng}&maxRes=10000&min=1&token={token}'
}

CYCLOCITY_ENDPOINT = "https://abo-{code}.cyclocity.fr"

TOKEN = None

geocoder = GoogleGeocoder()

cyclocity_data = {
    "system": "cyclocity",
    "class": "Cyclocity",
    "instances": []
}

parser = argparse.ArgumentParser(description = 'Extract Cyclocity instances from JCD')
parser.add_argument('-o', metavar = "file", dest = 'outfile', default = None, 
                    help="Save output to the specified file")
parser.add_argument('-g','--geocode', action="store_true",
                    help="Use Google GeoCoder for lat/lng and better names")

parser.add_argument('--proxy', metavar = "host:proxy", dest = 'proxy', default = None,
                    help="Use host:port as a proxy for JCD calls")

args = parser.parse_args()

outfile = args.outfile

session = requests.session()

proxies = {}

if args.proxy is not None:
    proxies['http'] = args.proxy

def getUrl(action, **args):
    return '%s%s' % (MAIN, ACTIONS[action].format(**args))

def call(action, **args):
    if 'token' not in args and TOKEN is not None:
        args['token'] = TOKEN
    url = getUrl(action, **args)
    r = requests.get(url, proxies = proxies)
    return r.json()

def getToken():
    data = call('token')
    return data['token']

def fix_cergy(system):
    system['code'] = 'cergy'
    return system

def fix_valence(system):
    system['countryCode'] = 'ES'
    system['name'] = 'Valencia'
    return system

hacks = {
    'cergy-pontoise': fix_cergy,
    'valence': fix_valence,
}

country_hash = {
    'es': 'es',
    'fr': 'fr',
    'ru': 'ru',
    'jp': 'ja',
    'lt': 'lt'
}


def extract_instance( system ):
    if system['code'] in hacks:
        system = hacks[system['code']](system)
    addr = system['name']
    
    try:
        if not args.geocode:
            raise Exception
        print "Geocoding %s" % addr
        geodata = geocoder.get(addr)
        time.sleep(1)
        latitude = geodata[0].geometry.location.lat
        longitude = geodata[0].geometry.location.lng

        if system['countryCode'].lower() in country_hash:
            language = country_hash[system['countryCode'].lower()]
        else:
            language = 'en'
        print "Reverse geocoding for better City names in %s" % language
        geodata = geocoder.get((latitude, longitude), language = language)
        time.sleep(1)
        better_name = [component.long_name for component in geodata[1].address_components if 'locality' in component.types]
        if len(better_name) > 0:
            city = better_name[0]
        else:
            city = system['name']
    except Exception as excp:
        print "No geodata found for %s: %s" % (addr, excp)
        print "Setting lat/lng to 0.0 for human intervention"
        latitude = 0.0
        longitude = 0.0
        city = system['name']

    tag = slugify(system['comname'])
    if (tag == 'cyclocity'):
        tag = slugify(system['name'])

    return {
        "tag": tag,
        "root_url": CYCLOCITY_ENDPOINT.format(code = system['code']),
        "city": system['code'],
        "meta": {
            "name": system['comname'],
            "city": city,
            "country": system['countryCode'],
            "latitude": latitude,
            "longitude": longitude
        }
    }

print "Adquiring token..."
TOKEN = getToken()
print "Getting cities..."
cities = call('cities')
print "Got %d cities from cyclocity servers" % len(cities)

for city in cities:
    instance = extract_instance(city)
    if instance is not None:
        cyclocity_data['instances'].append(instance)

cyclocity_data['instances'] = sorted(cyclocity_data['instances'], key = lambda inst: inst['city'])

data = json.dumps(cyclocity_data, sort_keys = False, indent = 4)

if outfile is not None:
    f = open(outfile, 'w')
    f.write(data)
    f.close()
    print "%s file written" % outfile
else:
    print "---- OUTPUT ----"
    print data
