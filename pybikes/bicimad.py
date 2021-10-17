# -*- coding: utf-8 -*-
# Copyright (C) 2018, eskerda <eskerda@gmail.com>
# Copyright (C) 2021, Altonss (https://github.com/Altonss)
# Distributed under the LGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


COLORS = ['green', 'red', 'yellow', 'gray']


class Bicimad(BikeShareSystem):
    meta = {
        'system': 'bicimad',
        'company': 'Empresa Municipal de Transportes de Madrid, S.A.'
    }

    def __init__(self, tag, meta, feed_url):
        super(Bicimad, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))
        self.stations = [BicimadStation(s) for s in data['data']]

class BicimadStation(BikeShareStation):
    def __init__(self, data):
        super(BicimadStation, self).__init__()
        self.name = data['name']
        self.longitude, self.latitude = map(float, data['geometry']['coordinates'])        
        self.bikes = int(data['dock_bikes'])
        self.free = int(data['free_bases'])
        self.extra = {
            'number': data['number'],
            'uid': data['id'],
            'address': data['address'],
            'online': data['activate'] == 1 and data['no_available'] == 0,
            'slots': int(data['total_bases']),
            'light': COLORS[int(data['light'])]
        }
