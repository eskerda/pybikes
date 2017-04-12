# -*- coding: utf-8 -*-
# Copyright (C) 2015, David Kreitschmann <david@kreitschmann.de>
# Distributed under the AGPL license, see LICENSE.txt
import re
import json
import itertools
import time

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Callabike', 'CallabikeStation']

feed_url = 'https://www.callabike-interaktiv.de/rpc'

class Callabike(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'Call-A-Bike',
        'company': ['DB Rent GmbH']
    }

    def __init__(self, tag, meta):
        super(Callabike, self).__init__(tag, meta)

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        LAT = self.meta['latitude'];
        LON = self.meta['longitude'];

        BODY_DICT = {
            'method': "Map.listBikes",
            'params': [{
                'lat': LAT,
                'long': LON,
                'maxItems': 100,
                'radius': 100000
            }],
            'id': int(round(time.time() * 1000))
        }

        data = json.loads(
            scraper.request(feed_url, 'POST', data=json.dumps(BODY_DICT))
        )

        locations = data['result']['data']['Locations']
        self.stations = map(CallabikeStation, locations, itertools.repeat(self.meta['name'], len(locations)))


class CallabikeStation(BikeShareStation):
    def __init__(self, data, name):
        super(CallabikeStation, self).__init__()
        self.name = data['objectName']
        if self.name == "-":
            self.name = name
        self.latitude = float(data['Position']['Latitude'])
        self.longitude = float(data['Position']['Longitude'])
        self.bikes = int(data['totalVehicles'])
        self.free = data[u'FreeBikes'].__len__()
        self.extra = {
            'description': data['Description'],
            'isPedelec': data['isPedelec'],
            'isStation': data['isStation'],
            'objectId': data['objectId']
        }
