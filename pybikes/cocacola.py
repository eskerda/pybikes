# -*- coding: utf-8 -*-
# Copyright (C) Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['CocaCola', 'CocaColaStation']

FEED_URL = "https://www.bikeshare.ie/"
STATIONS_RGX = "var\ mapsfromcache\ =\ (.*?);"

class CocaCola(BikeShareSystem):

    sync = True

    meta = {
        'system': 'CocaCola',
        'company': 'The National Transport Authority'
    }

    def __init__(self, tag, meta):
        super(CocaCola, self).__init__(tag, meta)

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
            
        stations = []
        
        html = scraper.request(FEED_URL)
        stations_html = re.findall(STATIONS_RGX, html)
        data = json.loads(stations_html[0])

        for item in data[self.tag]:
            name = item['name']
            latitude = item['latitude']
            longitude = item['longitude']
            bikes = item['bikesAvailable']
            free = item['docksAvailable']
            extra = {
                'uid': item['stationId']
            }
            station = CocaColaStation(name, latitude, longitude, bikes, free, extra)
            stations.append(station)
        self.stations = stations

class CocaColaStation(BikeShareStation):
    def __init__(self, name, latitude, longitude, bikes, free, extra):
        super(CocaColaStation, self).__init__()

        self.name      = name
        self.latitude  = latitude
        self.longitude = longitude
        self.bikes     = bikes
        self.free      = free
        self.extra     = extra