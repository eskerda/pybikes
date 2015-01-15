# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from . import utils
from .contrib import TSTCache

__all__ = ['Nextbike', 'NextbikeStation']

BASE_URL = 'https://nextbike.net/maps/nextbike-live.xml?domains={domain}'
CITY_QUERY = '/markers/country/city[@uid="{uid}"]/place'

cache = TSTCache(delta=60)

class Nextbike(BikeShareSystem):
    sync = True

    meta = {
        'system': 'Nextbike',
        'company': 'Nextbike GmbH'
    }

    def __init__(self, tag, meta, domain, city_uid):
        super(Nextbike, self).__init__(tag, meta)
        self.url = BASE_URL.format(domain = domain)
        self.uid = city_uid

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper(cache)
        domain_xml = etree.fromstring(
            scraper.request(self.url).encode('utf-8'))
        places = domain_xml.xpath(CITY_QUERY.format(uid = self.uid))
        self.stations = filter(None, map(NextbikeStation, places))

class NextbikeStation(BikeShareStation):
    def __new__(cls, place_tree):
        # TODO: For now we are not going to track bikes roaming around
        if 'bike' in place_tree.attrib:
            if place_tree.attrib['bikes'] == "1":
                if place_tree.attrib['bike'] == "1":
                    return
        return super(NextbikeStation, cls).__new__(cls, place_tree)

    def __init__(self, place_tree):
        super(NextbikeStation, self).__init__(0)
        self.extra = {}

        # Some names are '1231-foo' and other are 'bar'
        # and some might be '1211-foo-bar-baz   -yeah- kill - me
        num_name_re = r'(?P<id>\d*)\s*\-?\s*(?P<name>\D+)'
        match = re.search(num_name_re, place_tree.attrib['name'])
        if match.group('id'):
            self.extra['uid'] = int(match.group('id'))
            if match.group('id') != place_tree.attrib['uid']:
                self.extra['internal_uid'] = int(place_tree.attrib['uid'])
        else:
            self.extra['uid'] = int(place_tree.attrib['uid'])
        self.name = match.group('name').strip()

        # Gotta be careful here, some nextbike services just count up to 5,
        # displaying 5+
        if place_tree.attrib['bikes'].endswith('+'):
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
            self.extra['bike_uids'] = map(int, place_tree.attrib['bike_numbers'].split(','))

