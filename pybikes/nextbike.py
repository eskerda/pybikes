# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re

from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Nextbike', 'NextbikeStation']

BASE_URL = 'https://nextbike.net/maps/nextbike-live.xml?domains={domain}'
CITY_QUERY = '/markers/country/city[@uid="{uid}"]/place'

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
            scraper = utils.PyBikesScraper()
        domain_xml = etree.fromstring(
            scraper.request(self.url).encode('utf-8'))
        places = domain_xml.xpath(CITY_QUERY.format(uid = self.uid))
        self.stations = map(NextbikeStation, places)

class NextbikeStation(BikeShareStation):
    def __init__(self, place_tree):
        super(NextbikeStation, self).__init__(0)
        self.extra = {}

        # Some names are '1231-foo' and other are 'bar'
        num_name = place_tree.attrib['name'].split('-')
        if len(num_name) > 1:
            self.extra['uid'] = num_name[0]
            self.name = num_name[1]
            if num_name[0] != place_tree.attrib['uid']:
                self.extra['internal_uid'] = place_tree.attrib['uid']
        else:
            self.name = num_name[0]
            self.extra['uid'] = place_tree.attrib['uid']

        # Gotta be careful here, some nextbike services just count up to 5,
        # displaying 5+
        if place_tree.attrib['bikes'].endswith('+'):
            self.bikes = int(place_tree.attrib['bikes'][:1])
            self.extra['bikes_approximate'] = True
        else:
            self.bikes = int(place_tree.attrib['bikes'])

        # Bike racks may or may not be there
        if 'bike_racks' in place_tree.attrib:
            self.free = place_tree.attrib['bike_racks']
        else:
            self.free = -1
            self.extra['slots_approximate'] = True
        self.latitude = float(place_tree.attrib['lat'])
        self.longitude = float(place_tree.attrib['lng'])
        if 'bike_numbers' in place_tree.attrib:
            self.extra['bike_uids'] = place_tree.attrib['bike_numbers'].split(',')

