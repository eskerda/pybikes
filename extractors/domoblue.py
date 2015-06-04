# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import os
import sys
import time
import json
import argparse
from collections import namedtuple
import re

from lxml import etree

from googlegeocoder import GoogleGeocoder
from slugify import slugify
from pybikes.utils import PyBikesScraper
from pybikes.domoblue import Domoblue

MAIN = 'http://clientes.domoblue.es/onroll/'
TOKEN_URL = 'generaMapa.php?cliente={service}&ancho=500&alto=700'
XML_URL = 'generaXml.php?token={token}&cliente={service}'
TOKEN_RE = 'generaXml\.php\?token\=(.*?)\&cliente'

geocoder = GoogleGeocoder()

CityRecord = namedtuple('CityRecord', 'city, country, lat, lng')

description = 'Extract DomoBlue instances from the main site'

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

proxies = {}

user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'

scraper = PyBikesScraper()
scraper.setUserAgent(user_agent)

sysdef = {
    "system": "domoblue",
    "class": "Domoblue",
    "instances": []
}

if args.proxy is not None:
    proxies['http'] = args.proxy
    scraper.setProxies(proxies)
    scraper.enableProxy()


def get_token(client_id):
    if 'Referer' in scraper.headers:
        del(scraper.headers['Referer'])
    url = MAIN + TOKEN_URL.format(service = client_id)
    data = scraper.request(url)
    token = re.findall(TOKEN_RE, data)
    scraper.headers['Referer'] = url
    return token[0]

def get_xml(client_id):
    token = get_token(client_id)
    url = MAIN + XML_URL.format(token = token, service = client_id)
    return scraper.request(url).encode('raw_unicode_escape').decode('utf-8')

def test_system_health(domo_sys):
    online = False
    for s in domo_sys.stations:
        online = s.extra['status']['online']
        if online:
            break
    return online

def google_reverse_geocode(lat, lng):
    country_info = lambda lst: lst[len(lst) - 1].short_name
    target = 'locality'

    if args.verbose:
        print "--- Javascript code for debugging output ---"
        print "    var geocoder = new google.maps.Geocoder()"
        print "    latlng = new google.maps.LatLng(%s,%s)" % (str(lat), str(lng))
        print "    geocoder.geocode({latLng:latlng}, function(res){console.log(res)})"

    info = geocoder.get((lat, lng),language = 'es')
    city_info = [i for i in info if target in i.types]
    if len(city_info) == 0:
        target = 'political'
        city_info = [i for i in info if target in i.types]
        if len(city_info) == 0:
            raise Exception
    else:
        city_info = city_info[0]

    city = city_info.address_components[0].long_name

    country = country_info(city_info.address_components)
    latitude = city_info.geometry.location.lat
    longitude = city_info.geometry.location.lng

    return CityRecord(city, country, latitude, longitude)

def extract_systems():
    xml_data = get_xml('todos')
    xml_dom = etree.fromstring(xml_data)
    systems = []
    for marker in xml_dom.xpath('//marker'):
        if marker.get('tipo') == 'pendiente':
            continue
        sys = Domoblue('foo', {}, int(marker.get('codigoCliente')))
        sys.update()
        online = True #test_system_health(sys)
        if args.verbose:  
            print "--- %s --- " % repr(marker.get('nombre'))
            print " Total stations: %d" % len(sys.stations)
            print " Health: %s" % (lambda b: 'Online' if b else 'Offline')(online)
        if not online:
            if args.verbose:
                print " %s is Offline, ignoring!\n" % repr(marker.get('nombre'))
            continue

        name = 'Onroll %s' % marker.get('nombre')
        slug = slugify(name)
        city = marker.get('nombre')
        latitude = marker.get('lat')
        longitude = marker.get('lng')
        country = 'ES'

        if args.geocode:
            time.sleep(1)
            try:
                city, country, latitude, longitude = google_reverse_geocode(latitude, longitude)
                name = 'Onroll %s' % city
            except Exception:
                print " No geocoding results for %s!!" % repr(name)
        system = {
            'tag': slug,
            'system_id': int(marker.get('codigoCliente')),
            'meta': {
                'name': name,
                'latitude': latitude,
                'longitude': longitude,
                'city': city,
                'country': 'ES'
            }
        }
        systems.append(system)
        if args.verbose:
            print " Appended!\n"
    return systems

instances = extract_systems()
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
