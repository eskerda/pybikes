# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import os
import sys
import time
import json
import argparse
from urlparse import urlparse
from collections import namedtuple

from googlegeocoder import GoogleGeocoder
from slugify import slugify
import pybikes

geocoder = GoogleGeocoder()

CityRecord = namedtuple('CityRecord', 'city, country, lat, lng')

description = 'Given a PyBikes instance file, fills undeclared values'

parser = argparse.ArgumentParser(description = description)

parser.add_argument('input', metavar = "input", 
                    type = argparse.FileType('r'), default = sys.stdin,
                    help="Input file")

parser.add_argument('-o', metavar = "output", dest = "output", 
                    type = argparse.FileType('w'), default = sys.stdout, 
                    help="Output file")

parser.add_argument('-v', action="store_true", dest = 'verbose', 
                    default = False, help="Verbose output for debugging (no progress)")

parser.add_argument('--proxy', metavar = "host:proxy", dest = 'proxy', 
                    default = None, help="Use host:port as a proxy for site calls")

parser.add_argument('--httpsproxy', metavar = "host:proxy", dest = 'httpsproxy', 
                    default = None, help="Use host:port as an HTTPS proxy for site calls")

parser.add_argument('--slugify', action="store_true", dest = 'slugify', 
                    default = False, help="Correct slugs, using the name as input")

parser.add_argument('--geocode', action="store_true", dest = 'geocode', 
                    default = False, help="Correct geodata using Google GeoCoder")

parser.add_argument('-f', action="store_true", dest = 'overwrite', 
                    default = False, help="Overwrite already set variables")

parser.add_argument('-i', action="store_true", dest = 'interactive', 
                    default = False, help="Interactive prompt to select between results")

args = parser.parse_args()

scraper = pybikes.utils.PyBikesScraper()

proxies = {}

prompts = {
    'slug': '\n--------------\n' + \
            '| Old: {old_tag}\n' + \
            '|---------------\n' + \
            '| New: {new_tag}\n' + \
            '----------------\n' + \
            'Overwrite? y/n/set: '
}

language = 'en'

metas = ['city', 'country']

def clearline(length):
    clearline = "\r" + "".join([" " for i in range(length)])
    sys.stderr.flush()
    sys.stderr.write(clearline)
    sys.stderr.flush()

def print_status(i, total, status):
    progress = "".join(["#" for step in range(i)]) + \
               "".join([" " for step in range(total-i)])
    status_pattern = "\r{0}/{1}: [{2}] {3}"
    output = status_pattern.format(i, total, progress, status)
    sys.stderr.flush()
    sys.stderr.write(unicode(output))
    sys.stderr.flush()
    if (i == total):
        sys.stderr.write('\n')
    return len(output)

def geocode(instance, systemCls, language):
    if args.verbose:
        sys.stderr.write("--- Geocoding %s ---- \n" % instance['tag'])
    bikesys = systemCls(** instance)

    latitude, longitude = [0.0, 0.0]
    if 'latitude' in instance['meta'] and 'longitude' in instance['meta']:
        latitude  = instance['meta']['latitude']
        longitude = instance['meta']['longitude']
    else:
        if args.verbose:
            sys.stderr.write("Updating system to get an initial lat/lng\n")
        bikesys.update(scraper)
        latitude  = bikesys.stations[0].latitude
        longitude = bikesys.stations[0].longitude
    if args.verbose:
        sys.stderr.write(" >>> %s, %s <<< \n" % (str(latitude), str(longitude)))
        sys.stderr.write("--- Javascript code for debugging output ---\n")
        sys.stderr.write("var geocoder = new google.maps.Geocoder()\n")
        sys.stderr.write("latlng = new google.maps.LatLng(%s,%s)\n" % (str(latitude), str(longitude)))
        sys.stderr.write("geocoder.geocode({latLng:latlng}, function(res){console.log(res)})\n")
    info = geocoder.get((latitude, longitude), language = language)
    if args.interactive:
        for index, address in enumerate(info):
            sys.stderr.write("%d: %s\n" % (index, address.formatted_address))
        sys.stderr.write("%d: Change language\n" % len(info))
        sys.stderr.write('\n')
        try:
            res = int(raw_input('Select option (number): '))
            if res == len(info):
                language = raw_input('New language? ')
                return geocode(instance, systemCls, language)
            elif res < len(info):
                address = info[res]
                metainfo = instance['meta']
                lat = address.geometry.location.lat
                lng = address.geometry.location.lng
                for index, el in enumerate(address.address_components):
                    sys.stderr.write("%d: %s\n" % (index, el.short_name))
                sys.stderr.write('Latitude: %s\n' % str(lat))
                sys.stderr.write('Longitude: %s\n' % str(lng))
                sys.stderr.write('\n')
                for meta in metas:
                    res = raw_input('Select the %s: ' % meta)
                    if ',' in res:
                        res = res.split(',')
                    else:
                        res = [res]
                    metainfo[meta] = ''
                    for i, r in enumerate(res):
                        r = int(r)
                        metainfo[meta] += address.address_components[r].short_name
                        if (i < len(res)-1):
                            metainfo[meta] += ', '
                metainfo['latitude'] = lat
                metainfo['longitude'] = lng
                instance['meta'] = metainfo
                return True
        except Exception as e:
            print e
            return geocode(instance, systemCls, language)

    if args.verbose:
        sys.stderr.write("\n")

def main():
    if args.proxy is not None:
        proxies['http'] = args.proxy
        scraper.enableProxy()

    if args.httpsproxy is not None:
        proxies['https'] = args.httpsproxy
        scraper.enableProxy()

    scraper.setProxies(proxies)

    if not args.slugify and not args.geocode:
        sys.stderr.write("Nothing to do, stopping\n")
        exit(0)

    data = json.loads(args.input.read())
    instances = data['instances']
    system = data['system']
    systemCls = eval('pybikes.' + data['class'])

    sys.stderr.write('Found %d instances for %s\n' % (len(instances), system))
    lastlen = 0

    if args.interactive and args.geocode:
        language = raw_input('Desired geocoding language? ')

    for i, instance in enumerate(instances):
        if not args.verbose:
            clearline(lastlen)
            lastlen = print_status(i+1, len(instances), \
                        "Testing %s" % repr(instance['meta']['name']))
        if 'name' not in instance['meta'] or instance['meta']['name'] == "":
            raise Exception("name not set in instance %s" % str(instance))
        if args.slugify:
            tag = slugify(instance['meta']['name'])
            r   = None
            if args.interactive:
                r = raw_input(prompts['slug'].format(old_tag = instance['tag'],
                                                     new_tag = tag))
                if r == 'set':
                    tag = raw_input("Set new tag: ")
                elif r == 'n':
                    continue
            if r != 'n' or args.overwrite or 'tag' not in instance or 'tag' == '':
                instance['tag'] = tag

        if args.geocode:
            geocode(instance, systemCls, language)
            time.sleep(1)

    corrected_data = json.dumps(data, sort_keys = False, indent = 4)
    args.output.write(corrected_data)
    args.output.write('\n')
    args.output.close()

if __name__ == "__main__":
    main()