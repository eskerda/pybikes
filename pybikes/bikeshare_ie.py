# -*- coding: utf-8 -*-
# Copyright (C) 2025, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from pybikes import PyBikesScraper

FEED_URL = 'https://apps.bikeshare.ie/rbs/resources/appapi/station/data/list'


class BikeshareIE(BikeShareSystem):
    authed = True

    meta = {
        'system': 'TFI Bikes',
        'company': ['The National Transport Authority']
    }

    sync = True

    def __init__(self, tag, meta, system_id, key):
        super(BikeshareIE, self).__init__(tag, meta)
        self.system_id = system_id
        self.key = key

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations = []

        headers = {
            'Authorization': 'Basic ' + str(self.key['token']),
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; ROCINANTE FIRE Build/9001',
        }

        payload = {'schemeId': str(self.system_id)}

        res = scraper.request(FEED_URL, method='POST', data=payload, headers=headers)
        data = json.loads(res)

        for item in data['data']:
            name = item['name']
            latitude = float(item['latitude'])
            longitude = float(item['longitude'])
            bikes = int(item['bikesAvailable'])
            free = int(item['docksAvailable'])
            extra = {
                'uid': item['stationId'],
                'slots': int(item['docksCount']),
                'name_ie': item['nameIrish']
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
