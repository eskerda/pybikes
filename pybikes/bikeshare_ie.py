# -*- coding: utf-8 -*-
# Copyright (C) Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

FEED_URL = "https://www.bikeshare.ie/"
STATIONS_RGX = "var\ mapsfromcache\ =\ (.*?\}\]\})"


class BikeshareIE(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Coca-Cola Zero® Bikes',
        'company': ['The National Transport Authority']
    }

    def __init__(self, tag, meta, system_id):
        super(BikeshareIE, self).__init__(tag, meta)
        self.system_id = system_id

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        stations = []

        html = scraper.request(FEED_URL)
        stations_html = re.findall(STATIONS_RGX, html)
        data = json.loads(stations_html[0])

        for item in data[self.system_id]:
            name = item['name']
            latitude = float(item['latitude'])
            longitude = float(item['longitude'])
            bikes = int(item['bikesAvailable'])
            free = int(item['docksAvailable'])
            extra = {
                'uid': item['stationId'],
                'slots': int(item['docksCount'])
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
