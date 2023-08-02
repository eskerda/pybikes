# -*- coding: utf-8 -*-
# Copyright (C) 2010-2023, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

class GiraSystem(BikeShareSystem):
    meta = {
        'system': 'Gira',
        'company': ['EMEL']
    }

    def __init__(self, tag, feed_url, meta):
        super( GiraSystem, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))
        self.stations = list(map(GiraStation, data['features']))


class GiraStation(BikeShareStation):
    def __init__(self, info):
        super(GiraStation, self).__init__()

        self.latitude = float(info['geometry']['coordinates'][0][1])
        self.longitude = float(info['geometry']['coordinates'][0][0])
        self.name = info['properties']['desig_comercial']
        self.bikes = int(info['properties']['num_bicicletas'])
        self.free = int(info['properties']['num_docas']) - self.bikes
        self.extra = {
            'uid': info['properties']['id_expl'],
            'slots': info['properties']['num_docas'],
            'status': info['properties']['estado'],
            'online': info['properties']['estado'] == 'active',
        }
