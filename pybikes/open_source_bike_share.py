# -*- coding: utf-8 -*-
# Copyright (C) Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes import utils


class OpenSourceBikeShare(BikeShareSystem):

    meta = {
        'system': 'OpenSourceBikeShare',
        "company": ["Open Source Bike Share"]
    }

    def __init__(self, tag, meta, feed_url):
        super(OpenSourceBikeShare, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))

        for station in data:

            longitude = float(station['lon'])
            latitude = float(station['lat'])

            name = station['standName']
            free = None
            bikes = int(station['bikecount'])

            extra = {
                'photo': station['standPhoto'],
                'description': station['standDescription'],
                'uid': int(station['standId'])
            }

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)

        self.stations = stations
