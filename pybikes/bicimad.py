# -*- coding: utf-8 -*-
# Copyright (C) 2018, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


COLORS = ['green', 'red', 'yellow', 'gray']


class Bicimad(BikeShareSystem):

    authed = True

    meta = {
        'system': 'bicimad',
        'company': 'Empresa Municipal de Transportes de Madrid, S.A.'
    }

    headers = {
        'User-Agent': 'okhttp/3.3.0',
        'Content-Type': 'application/json',
    }

    endpoint = 'https://api.bicimad.com/emt_v10/'

    def __init__(self, tag, meta, key):
        super(Bicimad, self).__init__(tag, meta)
        self.app_hash = key

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        scraper.headers.update(self.headers)

        payload = {
            'app_hash': self.app_hash,
            'compressed': True,
            'function': 'get_stations',
            'station': '0',
        }

        response = scraper.request(self.endpoint, 'POST',
                                   data=json.dumps(payload))
        # Double JSON is always better than single JSON :)
        data = json.loads(json.loads(response)['data'])
        self.stations = [BicimadStation(s) for s in data['stations']]


class BicimadStation(BikeShareStation):
    def __init__(self, data):
        super(BicimadStation, self).__init__()
        self.name = data['name']
        self.latitude = float(data['latitude'])
        self.longitude = float(data['longitude'])
        self.bikes = int(data['dock_bikes'])
        self.free = int(data['free_bases'])
        self.extra = {
            'number': data['number'],
            'uid': data['id'],
            'address': data['address'],
            'online': data['activate'] == 1 and data['no_available'] == 0,
            'slots': int(data['total_bases']),
            'light': COLORS[int(data['light'])]
        }
