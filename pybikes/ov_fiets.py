# -*- coding: utf-8 -*-
# Copyright (C) 2024, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

FEED_URL = 'https://gateway.apiportal.ns.nl/places-api/v2/nearbyme'

REQ_DATA = {
    'minLat': 50.2876,
    'minLng': 2.7109,
    'maxLat': 53.8857,
    'maxLng': 7.9541,
    'zoomLevel': 9,
    'limit': 500,
    'filterTypes': ['OV_FIETS'],
    'appVersionCapabilities': ['DLF-Tier', 'DLS-Check', 'DLA-GreenWheels'],
    'enableSubfilters': True,
}

class OvFiets(BikeShareSystem):

    authed = True

    def __init__(self, key, * args, ** kwargs):
        self.key = key
        super(OvFiets, self).__init__(* args, ** kwargs)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        headers = {
            'X-MmVehicleExtra': 'false',
            'Ocp-Apim-Subscription-Key': self.key,
        }

        data = json.loads(scraper.request(FEED_URL, params=REQ_DATA, headers=headers))
        self.stations = list(map(self.parse_station, data['locations']))

    def parse_station(self, data):
        bikes = next(iter(re.findall(r'\d+', data['description']['subDescription'])), 0)
        uid = re.match(r'.*-(\w+)\s*$', data['id']['value']).group(1)
        return BikeShareStation(
            name=data['description']['full'],
            latitude=data['lat'],
            longitude=data['lng'],
            bikes=int(bikes),
            extra={'uid': uid},
        )
