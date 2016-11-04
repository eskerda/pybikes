# -*- coding: utf-8 -*-
# Copyright (C) 2015, bparmentier <dev@brunoparmentier.be>
# Copyright (C) 2016, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Copyright (C) 2016, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes import utils


class EasyBike(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'EasyBike',
        'company': ['Brainbox Technology', 'Smoove SAS']
    }

    feed_url = 'http://reseller.easybike.gr/{city_uid}/api.php'

    def __init__(self, tag, meta, city_uid, bbox=None):
        super(EasyBike, self).__init__(tag, meta)
        self.feed_url = EasyBike.feed_url.format(city_uid=city_uid)
        self.bbox = bbox

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        stations = self.get_stations(data)
        if self.bbox:
            stations = utils.filter_bounds(stations, None, self.bbox)
        self.stations = list(stations)

    def get_stations(self, data):
        for station in data['stations']:
            name = station['description']
            longitude = float(station['lng'])
            latitude = float(station['lat'])
            bikes = int(station['free_bikes'])
            free = int(station['free_spaces'])
            extra = {
                'slots': int(station['total_spaces'])
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            yield station
