# -*- coding: utf-8 -*-
# Copyright (C) Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes import utils
from pybikes.open_source_bike_share import OpenSourceBikeShare


class OpenSourceBikeShareV2(OpenSourceBikeShare):
    authed = True

    def __init__(self, tag, meta, feed_url, key):
        super().__init__(tag, meta, feed_url)
        self.key = key

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        stations = []

        scraper.headers.update({
            'Authorization': 'Bearer %s' % self.key,
        })

        data = json.loads(scraper.request(self.feed_url))

        print(scraper.last_request)

        for station in data:
            longitude = float(station.get('lon') or station['longitude'])
            latitude = float(station.get('lat') or station['latitude'])

            name = station['standName']
            free = None
            bikes = int(station.get('bikecount') or station['bikeCount'])

            if 'slotcount' in station:
                free = int(station['slotcount'])

            extra = {
                'uid': int(station['standId']),
                'photo': station.get('standPhoto'),
                'description': station.get('standDescription'),
            }

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)

        self.stations = stations
