# -*- coding: utf-8 -*-
# Copyright (C) 2015, bparmentier <dev@brunoparmentier.be>
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils
from .contrib.tstcache import TSTCache

__all__ = ['EasyBike', 'EasyBikeStation']

BASE_URL = 'http://api.easybike.gr/cities.php'

cache = TSTCache(delta=60)

class EasyBike(BikeShareSystem):
    sync = True

    meta = {
        'system': 'EasyBike',
        'company': 'Brainbox Technology'
    }

    def __init__(self, tag, meta, city_uid):
        super(EasyBike, self).__init__(tag, meta)
        self.url = BASE_URL
        self.uid = city_uid

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper(cache)

        data = json.loads(scraper.request(self.url))
        for city in data:
            if city['city'] == self.uid:
                rawstations = city['stations']
                break

        if rawstations is None:
            raise Exception('City not found')

        stations = []
        for rawstation in rawstations:
            try:
                station = EasyBikeStation(rawstation)
            except Exception:
                continue
            stations.append(station)
        self.stations = stations

class EasyBikeStation(BikeShareStation):
    def __init__(self, info):
        super(EasyBikeStation, self).__init__()
        self.name = info['name']
        self.bikes = int(info['BikesAvailable'])
        self.free = int(info['DocksAvailable'])
        self.latitude = float(info['lat'])
        self.longitude = float(info['lng'])
        self.extra = {
            'slots': int(info['TotalDocks']),
        }

        if self.latitude is None or self.longitude is None:
            raise Exception('A station needs a lat/lng to be defined!')
        if self.latitude == 0 and self.longitude == 0:
            raise Exception('A station can\'t be located in Atlantic Ocean!')

