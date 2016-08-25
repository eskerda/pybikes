# -*- coding: utf-8 -*-
# Copyright (C) Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Hourbike']

RGX_MARKERS = r'setConfig\(\'StationsData\',(\[.*\])\);'

class Hourbike(BikeShareSystem):

    meta = {
        'system': 'Hourbike',
        'company': 'Hourbike'
    }

    def __init__(self, tag, feed_url, meta):
        super(Hourbike, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        self.stations = []
        html = scraper.request(self.feed_url)

        raw_data = re.search(RGX_MARKERS, html).group(1)
        stations_data = json.loads(raw_data)

        for station in stations_data:
            latitude = float(station['Latitude'])
            longitude = float(station['Longitude'])

            name = station['Name']
            bikes = int(station['TotalAvailableBikes'])
            free = int(station['TotalLocks']) - bikes
            extra = {
                'uid': station['id']
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            self.stations.append(station)