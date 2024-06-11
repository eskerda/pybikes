# -*- coding: utf-8 -*-
# Copyright (C) 2024, eskerda <eskerda@gmail.com>
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the LGPL license, see LICENSE.txt

import re
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


BASE_URL = 'https://kolumbus-sanntidsskjerm-backend-prod.azurewebsites.net/entur/city-bikes'


class Kolumbus(Bounded, BikeShareSystem):
    meta = {
        'system': 'kolumbus',
        'company': ['Kolumbus']
    }

    def __init__(self, tag, meta, bbox):
        super(Kolumbus, self).__init__(tag, meta, bounds=bbox)
        self.bbox = bbox

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        data = json.loads(scraper.request(BASE_URL))

        stations = []
        for station in data:
            stations.append(KolumbusStation(station))

        self.stations = stations


class KolumbusStation(BikeShareStation):
    def __init__(self, data):
        super(KolumbusStation, self).__init__()

        self.latitude = float(data['latitude'])
        self.longitude = float(data['longitude'])
        self.name = data['name']

        bikes = int(data['available'])
        slots = int(data['capacity'])

        self.bikes = bikes
        # there are only a few charging slots available per station
        # but people can leave bikes close if there is no room
        # this means we could have more bikes than slots: in that case count it as 0
        self.free = max(slots - bikes, 0)

        # ids are like 'YKO:Station:42'
        number = next(map(int, (re.findall(r'Station:(\d+)$', data['id']))), None)

        self.extra = {
            'has_ebikes': True,
            'slots': slots,
            'uid': data['id'],
            'number': number,
        }
