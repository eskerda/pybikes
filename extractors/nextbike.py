# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import argparse
import codecs
import json
import sys

from lxml import etree
import requests
from slugify import slugify


FEEDS = "https://nextbike.net/maps/nextbike-live.xml?domains={domain}"

parser = argparse.ArgumentParser()

parser.add_argument('--domain', type=str, default="", dest="domain")
parser.add_argument('-o', metavar="file", dest="out",
                    type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument('-v', action="store_true", dest="verbose", default=False)
parser.add_argument('-vv', action="store_true", dest="ultraverbose",
                    default=False)
parser.add_argument('--base', metavar="file", dest="baseinst",
                    default=None, type=argparse.FileType('r'))

args = parser.parse_args()

UTF8Writer = codecs.getwriter('utf8')
sys.stderr = UTF8Writer(sys.stderr)
filewriter = UTF8Writer(args.out)

if args.baseinst:
    sysdef = json.loads(args.baseinst.read())
else:
    sysdef = {
        "system": "nextbike",
        "class": "Nextbike",
        "instances": []
    }


class Nextfeed(object):
    def __new__(cls, city_tree, domain=""):
        stations = city_tree.xpath('place')
        suspected_bikes = [st for st in stations if Nextfeed.is_flexbike(st)]
        net_stations = [st for st in stations if not Nextfeed.is_flexbike(st)]
        if args.ultraverbose:
            sys.stderr.write("%s\n" % city_tree.attrib['name'])
            sys.stderr.write("=" * len(city_tree.attrib['name']))
            sys.stderr.write("\n")
            sys.stderr.write(u"├ Stations: %d\n" % len(stations))
            sys.stderr.write(u"├ Flex Bikes: %d\n" % len(suspected_bikes))
            sys.stderr.write(u"├ Net Stations: %d\n" % len(net_stations))
            sys.stderr.write("\n\n")
        return super(Nextfeed, cls).__new__(cls, city_tree, domain)

    def __init__(self, city_tree, domain=""):
        self.domain = domain
        self.tag = slugify(city_tree.attrib['name'])
        self.name = city_tree.attrib['name']
        self.city_uid = int(city_tree.attrib['uid'])

    def out(self):
        return {
            "domain": self.domain,
            "tag": self.tag,
            "meta": {
                "name": self.name
            },
            "city_uid": self.city_uid
        }

    @staticmethod
    def is_flexbike(station_tree):
        if 'bike' in station_tree.attrib:
            if station_tree.attrib['bikes'] == "1":
                if station_tree.attrib['bike'] == "1":
                    return True
        if 'spot' in station_tree.attrib:
            if station_tree.attrib['spot'] == "1":
                return False
            else:
                return True
        if 'BIKE' in station_tree.attrib['name']:
            return True
        return False

    @staticmethod
    def print_station(station_tree, prefix=""):
        for attrib in station_tree.attrib:
            sys.stderr.write(prefix)
            sys.stderr.write(u"├ %s: %s\n" % (
                attrib, station_tree.attrib[attrib])
            )


def get_systems(domain=""):
    nextfeed = etree.fromstring(
        requests.get(FEEDS.format(domain=domain)).text.encode('utf-8'))
    cities = nextfeed.xpath("/markers/country/city")
    new_cities = []
    for c in cities:
        if 'city_uid' in c.attrib:
            uid = int(c.attrib['city_uid'])
        elif 'uid' in c.attrib:
            uid = int(c.attrib['uid'])
        else:
            raise Exception("This city has no uid")
        found = next(
            (i for i in sysdef['instances'] if i['city_uid'] == uid), None)
        if not found:
            new_cities.append(c)
    if args.verbose:
        sys.stderr.write(">> Found %d new cities in %s\n" % (
            len(new_cities), domain))
    systems = map(lambda c: Nextfeed(c, domain), new_cities)
    return systems

for domain in args.domain.split(','):
    systems = get_systems(domain)
    sysdef['instances'] += map(lambda sys: sys.out(), systems)

filewriter.write(json.dumps(sysdef, indent=4, separators=(',', ':')))
filewriter.write("\n")
