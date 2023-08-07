# -*- coding: utf-8 -*-
# Copyright (C) 2018, eskerda <eskerda@gmail.com>
# Copyright (C) 2021, Altonss (https://github.com/Altonss)
# Copyright (C) 2022, eUgEntOptIc44 (https://github.com/eUgEntOptIc44)
# Distributed under the LGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.contrib import TSTCache


COLORS = ['green', 'red', 'yellow', 'gray']
AUTH_URL = 'https://openapi.emtmadrid.es/v2/mobilitylabs/user/login/'
FEED_URL = 'https://openapi.emtmadrid.es/v2/transport/bicimad/stations/'

cache = TSTCache(delta=3600)


class Bicimad(BikeShareSystem):
    authed = True

    meta = {
        'system': 'bicimad',
        'company': 'Empresa Municipal de Transportes de Madrid, S.A.',
        'source': 'https://mobilitylabs.emtmadrid.es/',
    }

    def __init__(self, tag, meta, key):
        super(Bicimad, self).__init__(tag, meta)
        self.key = key

    @staticmethod
    def authorize(scraper, key):
        request = scraper.request

        headers = {
            'passkey': key['passkey'],
            'x-clientid': key['clientid'],
        }
        accesstoken_content = scraper.request(AUTH_URL, headers=headers)
        accesstoken = json.loads(accesstoken_content)['data'][0]['accessToken']

        def _request(*args, **kwargs):
            headers = kwargs.get('headers', {})
            headers.update({'accesstoken': accesstoken})
            kwargs['headers'] = headers
            return request(*args, **kwargs)

        scraper.request = _request

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper(cache)

        Bicimad.authorize(scraper, self.key)

        scraper_content = scraper.request(FEED_URL, skip_cache=True)

        data = json.loads(scraper_content)

        self.stations = [BicimadStation(s) for s in data['data']]


class BicimadStation(BikeShareStation):
    def __init__(self, data):
        super(BicimadStation, self).__init__()
        self.name = data['name']
        self.longitude = float(data['geometry']['coordinates'][0])
        self.latitude = float(data['geometry']['coordinates'][1])
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
