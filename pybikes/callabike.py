# -*- coding: utf-8 -*-
# Copyright (C) 2015, David Kreitschmann <david@kreitschmann.de>
# Distributed under the AGPL license, see LICENSE.txt
import re
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Callabike', 'CallabikeStation']

feed_url = 'https://www.callabike-interaktiv.de/rpc'

class Callabike(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'Call-A-Bike_new',
        'company': ['DB Rent GmbH_new']
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
            'id': 1491984844993
        }

        data = json.loads(
            scraper.request(feed_url, 'POST', data=json.dumps(BODY_DICT))
        )

        self.stations = map(CallabikeStation, data['result']['data']['Locations'])


class CallabikeStation(BikeShareStation):
    def __init__(self, data):
        super(CallabikeStation, self).__init__()
        self.name = data['objectName']
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
