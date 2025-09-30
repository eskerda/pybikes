# -*- coding: utf-8 -*-
# Copyright (C) 2025, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json
from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

FEED_URL = 'https://batumvelo.ge/api/client/public/parking'

class Batumvelo(BikeShareSystem):
    sync = True
   
    def update(self, scraper = None):
        scraper = scraper or PyBikesScraper()

        stations = []
        data = json.loads(scraper.request(FEED_URL,headers={'Accept': 'application/json'}))
        for item in data:
            station = BatumveloStation(item)
            stations.append(station)

        self.stations = stations

class BatumveloStation(BikeShareStation):
    def __init__(self, item):
        super(BatumveloStation, self).__init__()

        self.name = item['name']
        self.longitude = item['lng']
        self.latitude = item['lat']

        self.bikes = 0
        self.free = 0

        self.extra = {
            'online': item['type'] == 'ALLOW',
        }
