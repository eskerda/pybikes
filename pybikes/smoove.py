# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) 2019, Louis Turpinat <turpinat.louis@gmail.com>
# Copyright (C) 2016, Lluis Esquerda <eskerda@gmail.com>
# Copyright (C) 2015, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class CityBikeLima(BikeShareSystem):
    
    sync = True

    def __init__(self, tag, feed_url, meta):
        super(CityBikeLima, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []
        data = json.loads(scraper.request(self.feed_url))
        data = data['response']

        for item in data:
            name = item['name']

            latitude, longitude = item['coordinates']
            latitude = float(latitude)
            longitude = float(longitude)

            bikes = int(item['avl_bikes'])
            free = int(item['free_slots'])

            extra = {
                'uid': item['nid'], 
                'slots': int(item['total_slots'])
            }

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
