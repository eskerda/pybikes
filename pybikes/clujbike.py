# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Clujbike(BikeShareSystem):

    meta = {
        'system': 'Clujbike',
        'company': ['Municipiul Cluj-Napoca']
    }

    def __init__(self, tag, feed_url, meta):
        super(Clujbike, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        raw = scraper.request(self.feed_url)

        data = re.search(r'var stations = (\[.*?\]);', raw).group(1)

        stations = []

        for station in json.loads(data):
            stations.append(ClujBikeStation(station))

        self.stations = stations


class ClujBikeStation(BikeShareStation):
    def __init__(self, data):
        super(ClujBikeStation, self).__init__()

        self.name = data['StationName']
        self.latitude = float(data['Latitude'])
        self.longitude = float(data['Longitude'])

        self.bikes = int(data['OcuppiedSpots'])
        self.free = int(data['EmptyDoors'])
        self.status = 'offline' if data['Status'] == 'Offline' else 'online'
        self.extra = {
            'address': data['Address'],
            'status': self.status
        }
