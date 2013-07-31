# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import os
import sys
import time
import json
import argparse
import unidecode
from array import array
from urlparse import urlparse
from collections import namedtuple

import requests
from googlegeocoder import GoogleGeocoder
from slugify import slugify
from pyquery import PyQuery as pq
from pybikes import BCycleSystem, BCycleStation

MAIN = 'http://www.bcycle.com/'
SYS_SELECTOR = 'div.HomePage_TopMenuContent li.special ul li[class!=nav-vote] a'

geocoder = GoogleGeocoder()

CityRecord = namedtuple('CityRecord', 'city, country, lat, lng')

description = 'Extract BCycle instances from the main site'

parser = argparse.ArgumentParser(description = description)

parser.add_argument('-o', metavar = "file", dest = 'outfile', default = None, 
                    help="Save output to the specified file")
parser.add_argument('-g','--geocode', action="store_true",
                    help="Use Google GeoCoder for lat/lng and better names")

parser.add_argument('--proxy', metavar = "host:proxy", dest = 'proxy', 
                    default = None, help="Use host:port as a proxy for site calls")

parser.add_argument('-v', action="store_true", dest = 'verbose', 
                    default = False, help="Verbose output for debugging (no progress)")

args = parser.parse_args()

outfile = args.outfile

session = requests.session()

proxies = {}

if args.proxy is not None:
    proxies['http'] = args.proxy

"""
{
    "tag": "boulder",
    "system": "boulder",
    "meta": {
        "name": "Boulder B-Cycle",
        "city": "Boulder, CO",
        "country": "USA",
        "latitude": 40.0149856,
        "longitude": -105.2705455
    }
}
"""

sysdef = {
    "system": "bcycle",
    "class": "BCycleSystem",
    "instances": []
}

def extract_systems(site):
    sys_selector = 'div.HomePage_TopMenuContent li.special ul li[class!=nav-vote] a'
    fuzz_systems = pq(site)(SYS_SELECTOR)
    systems = []
    for system in fuzz_systems:
        name = pq(system).text()
        url = pq(system).attr('href')
        systems.append({'name': name,'url': url})
    return systems

def google_reverse_geocode(lat, lng):
    state_info = lambda lst: lst[len(lst) - 2].short_name
    country_info = lambda lst: lst[len(lst) - 1].short_name
    target = 'locality'

    if args.verbose:
        print "--- Javascript code for debugging output ---"
        print "    var geocoder = new google.maps.Geocoder()"
        print "    latlng = new google.maps.LatLng(%s,%s)" % (str(lat), str(lng))
        print "    geocoder.geocode({latLng:latlng}, function(res){console.log(res)})"

    info = geocoder.get((lat, lng),language = 'en')
    city_info = [i for i in info if target in i.types]
    if len(city_info) == 0:
        raise Exception
    else:
        city_info = city_info[0]

    city_name = city_info.address_components[0].long_name
    state = state_info(city_info.address_components)
    city = "%s, %s" % (city_name, state)

    country = country_info(city_info.address_components)
    latitude = city_info.geometry.location.lat
    longitude = city_info.geometry.location.lng

    return CityRecord(city, country, latitude, longitude)

def extract_system( data ):
    system = BCycleSystem(tag = 'foo', meta = {'name': data['name']},
                          feed_url = data['url'])
    try:
        system.update()
    except Exception:
        return None
    if len(system.stations) == 0:
        return None

    tag = urlparse(data['url']).netloc.split('.')[0]
    lat = system.stations[0].latitude
    lng = system.stations[0].longitude
    city = ''
    country = ''
    if args.geocode:
        if args.verbose:
            print "---> Geocoding %s" % data['name']
        try:
            city, country, lat, lng = google_reverse_geocode(lat, lng)
        except Exception:
            print "No geocoding results for %s" % data['name']
        time.sleep(1)

    instance = {
        'tag': tag,
        'feed_url': data['url'],
        'meta': {
            'name': data['name'],
            'city': city,
            'country': country,
            'latitude': lat,
            'longitude': lng
        }
    }

    return instance


def print_status(i, total, progress, status):
    status_pattern = "\r{i}/{total}: [{progress}] {status}"
    output = status_pattern.format(
        i = i+1, total = total, progress = progress.tostring(), status = status)
    sys.stdout.flush()
    sys.stdout.write("\r                                                              ")
    sys.stdout.flush()
    sys.stdout.write(unicode(output))
    sys.stdout.flush()


data = requests.get(MAIN, proxies = proxies)
systems = extract_systems(data.text)
print "Found %d systems!" % len(systems)
instances = []

progress = array('c','')
for p in range(len(systems)):
    progress.append(' ')

for i, system in enumerate(systems):
    progress[i] = '#'
    if not args.verbose:
        print_status(i, len(systems), progress, "%s" % system['name'])
    instance = extract_system(system)
    if instance is not None:
        instances.append(instance)
        if args.verbose:
            print instance

print "\n%d/%d systems are valid!" % (len(instances), len(systems))
sysdef['instances'] = sorted(instances, key = lambda inst: inst['tag'])

data = json.dumps(sysdef, sort_keys = False, indent = 4)

if outfile is not None:
    f = open(outfile, 'w')
    f.write(data)
    f.close()
    print "%s file written" % outfile
else:
    print "---- OUTPUT ----"
    print data
