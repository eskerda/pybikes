# -*- coding: utf-8 -*-
# Copyright (C) Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['Pronto', 'ProntoStation']

class Pronto(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Pronto',
        "company": ["Pronto!", 
                    "Alta Bicycle Share, Inc"]
    }

    def __init__(self, tag, feed_url, meta):
        super(Pronto, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
            
        stations = []
        
        data = json.loads(scraper.request(self.feed_url))
        # Each station is
        # {
        #     "id":1,
        #     "s":"3rd Ave & Broad St",
        #     "n":"BT-01",
        #     "st":1,
        #     "b":false,
        #     "su":false,
        #     "m":false,
        #     "lu":1444910420300,
        #     "lc":1444910706468,
        #     "bk":true,
        #     "bl":true,
        #     "la":47.618418,
        #     "lo":-122.350964,
        #     "da":9,
        #     "dx":0,
        #     "ba":8,
        #     "bx":1
        # }
        for item in data['stations']:
            name = item['s']
            latitude = item['la']
            longitude = item['lo']
            bikes = item['ba']
            free = item['da']
            extra = {
                'uid' : item['n']
            }
            station = ProntoStation(name, latitude, longitude,
                                    bikes, free, extra)
            stations.append(station)
        self.stations = stations

class ProntoStation(BikeShareStation):
    def __init__(self, name, latitude, longitude, bikes, free, extra):
        super(ProntoStation, self).__init__()

        self.name       = name
        self.latitude   = latitude
        self.longitude  = longitude
        self.bikes      = bikes
        self.free       = free
        self.extra      = extra