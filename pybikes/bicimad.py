# -*- coding: utf-8 -*-
# Copyright (C) 2018, eskerda <eskerda@gmail.com>
# Copyright (C) 2021, Altonss (https://github.com/Altonss)
# Copyright (C) 2022, eUgEntOptIc44 (https://github.com/eUgEntOptIc44)
# Distributed under the LGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.contrib import TSTCache


PASSKEY = 'C3D0E659D8D397782B414AB6FCC477B5C727435FE91E72069D34CEBB2C1491B3B8563FDAC043EA704660C0E87E6FE503C39D38FF43F7447563B1E437B349ACEC'
CLIENTID = '8ff527f9-f85b-45ef-b1b2-bd9eb59e0fff'
COLORS = ['green', 'red', 'yellow', 'gray']

cache = TSTCache(delta=3600)


class Bicimad(BikeShareSystem):
    meta = {
        'system': 'bicimad',
        'company': 'Empresa Municipal de Transportes de Madrid, S.A.'
    }

    def __init__(self, tag, meta, feed_url):
        super(Bicimad, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        access_token_scraper = PyBikesScraper(cache)
        access_token_content = access_token_scraper.request(
            'https://openapi.emtmadrid.es/v2/mobilitylabs/user/login/',
            headers={'passkey': PASSKEY, 'x-clientid': CLIENTID}
        )
        access_token = json.loads(access_token_content)['data'][0]['accessToken']

        scraper_content = scraper.request(self.feed_url, headers={
            'accesstoken': access_token
        })

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
