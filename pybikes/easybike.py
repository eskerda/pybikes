# -*- coding: utf-8 -*-
# Copyright (C) 2015, bparmentier <dev@brunoparmentier.be>
# Copyright (C) 2016, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes import utils
from contrib import TSTCache

__all__ = ['EasyBike']


cache = TSTCache(delta=60)


class EasyBike(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'EasyBike',
        'company': ['Brainbox Technology', 'Smoove SAS']
    }

    feed_url = 'http://reseller.easybike.gr/{city_uid}/api.php'

    def __init__(self, tag, meta, city_uid):
        super(EasyBike, self).__init__(tag, meta)
        self.feed_url = EasyBike.feed_url.format(city_uid=city_uid)

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper(cache)

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        for station in data['stations']:
            name = station['description']
            longitude = float(station['lng'])
            latitude = float(station['lat'])
            # Skip some junk stations present in athens
            if latitude == 51.43 and longitude == 5.48:
                continue
            bikes = int(station['free_bikes'])
            free = int(station['free_spaces'])
            extra = {
                'slots': int(station['total_spaces'])
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
