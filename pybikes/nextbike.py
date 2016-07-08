# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json
from lxml import etree

from shapely.geometry import Point, box

from .base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper
from pybikes.contrib import TSTCache

__all__ = ['Nextbike', 'NextbikeStation']

BASE_URL = 'https://{hostname}/maps/nextbike-live.xml?domains={domain}&get_biketypes=1'
CITY_QUERY = '/markers/country/city[@uid="{uid}"]/place'

cache = TSTCache(delta=60)


class Nextbike(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'Nextbike',
        'company': 'Nextbike GmbH'
    }

    def __init__(self, tag, meta, domain, city_uid, hostname = 'nextbike.net', bbox = None):
        super(Nextbike, self).__init__(tag, meta)
        self.url = BASE_URL.format(hostname=hostname, domain=domain)
        self.uid = city_uid
        self.bbox = None
        if bbox:
            self.bbox = box(bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1])

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper(cache)
        domain_xml = etree.fromstring(
            scraper.request(self.url).encode('utf-8'))
        places = domain_xml.xpath(CITY_QUERY.format(uid=self.uid))
        self.stations = map(NextbikeStation, self.filter_stations(places))

    def filter_stations(self, places):
        for place in places:
            # TODO: For now we are not going to track bikes roaming around
            if 'bike' in place.attrib:
                if place.attrib['bikes'] == "1" and place.attrib['bike'] == "1":
                    continue
            if self.bbox:
                lat = float(place.attrib['lat'])
                lng = float(place.attrib['lng'])
                coord = Point(lng, lat)
                if not self.bbox.contains(coord):
                    continue
            yield place


class NextbikeStation(BikeShareStation):
    def __init__(self, place_tree):
        super(NextbikeStation, self).__init__()
        self.extra = {}

        # Some names are '1231-foo' and other are 'bar'
        # and some might be '1211-foo-bar-baz   -yeah- kill - me
        num_name_re = r'(?P<id>\d*)\s*\-?\s*(?P<name>\D+)'
        match = re.search(num_name_re, place_tree.attrib['name'])
        if match:
            if match.group('id'):
                self.extra['uid'] = int(match.group('id'))
                if match.group('id') != place_tree.attrib['uid']:
                    self.extra['internal_uid'] = int(place_tree.attrib['uid'])
            else:
                self.extra['uid'] = int(place_tree.attrib['uid'])
            self.name = match.group('name').strip()
        else:
            self.name = place_tree.attrib['name']
            if 'number' in place_tree.attrib:
                self.extra['uid'] = place_tree.attrib['number']
                self.extra['internal_uid'] = place_tree.attrib['uid']
            else:
                self.extra['uid'] = place_tree.attrib['uid']

        # Gotta be careful here, some nextbike services just count up to 5,
        # displaying 5+. Trying to use the available bike_types count instead.
        if place_tree.attrib['bikes'].endswith('+'):
            if 'bike_types' in place_tree.attrib:
                bike_types = json.loads(place_tree.attrib['bike_types'])
                self.bikes = sum(bike_types.values())
            else:
                self.bikes = int(place_tree.attrib['bikes'][:1])
                self.extra['bikes_approximate'] = True
        else:
            self.bikes = int(place_tree.attrib['bikes'])

        # Bike racks may or may not be there
        if 'bike_racks' in place_tree.attrib:
            self.free = int(place_tree.attrib['bike_racks']) - self.bikes
            self.extra['slots'] = place_tree.attrib['bike_racks']
        else:
            self.free = -1
            self.extra['slots_approximate'] = True
        self.latitude = float(place_tree.attrib['lat'])
        self.longitude = float(place_tree.attrib['lng'])
        if 'bike_numbers' in place_tree.attrib:
            self.extra['bike_uids'] = map(
                int,
                place_tree.attrib['bike_numbers'].split(',')
            )
