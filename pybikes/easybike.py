# -*- coding: utf-8 -*-
# Copyright (C) 2015, bparmentier <dev@brunoparmentier.be>
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils
from contrib import TSTCache

__all__ = ['EasyBike', 'EasyBikeStation']


cache = TSTCache(delta=60)

class EasyBike(BikeShareSystem):
    sync = True

    meta = {
        'system': 'EasyBike',
        'company': 'Brainbox Technology'
    }

    FEED_URL = 'http://api.easybike.gr/cities.php'

    def __init__(self, tag, meta, city_uid):
        super(EasyBike, self).__init__(tag, meta)
        self.uid = city_uid

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper(cache)

        networks = json.loads(scraper.request(EasyBike.FEED_URL))
        network = next((n for n in networks if n['city'] == self.uid), None)
        assert network, "%s city not found in easybike feed" % self.uid
        self.stations = map(EasyBikeStation, network['stations'])

class EasyBikeStation(BikeShareStation):
    def __init__(self, info):
        super(EasyBikeStation, self).__init__()
        self.name = info['name'].encode('utf8')
        self.bikes = int(info['BikesAvailable'])
        self.free = int(info['DocksAvailable'])
        self.latitude = float(info['lat'])
        self.longitude = float(info['lng'])
        self.extra = {
            'slots': int(info['TotalDocks']),
        }
