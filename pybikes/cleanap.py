# -*- coding: utf-8 -*-
# Copyright (C) 2014, iomartin <iomartin@iomartin.net>
# Distributed under the LGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Cleanap', 'CleanapStation']


class Cleanap(BikeShareSystem):
    sync = True
    meta = {
        'system': 'CallLock',
        'company': 'CleaNap'
    }

    def __init__(self, tag, meta, url):
        super(Cleanap, self).__init__(tag, meta)
        self.feed_url = url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))
        self.stations = map(CleanapStation, data['response_data'])


class CleanapStation(BikeShareStation):
    def __init__(self, data):
        super(CleanapStation, self).__init__()
        self.name = data['title']
        self.latitude = float(data['latitude'])
        self.longitude = float(data['longitude'])
        self.bikes = int(data['available_bikes'])
        self.free = int(data['available_locks'])
        self.extra = {
            'uid': data['station_id'],
            'address': data['address'],
            'postalCode': data['postalCode'],
            'online': data['status'] == 1,
            'slots': int(data['capacity'])
        }
