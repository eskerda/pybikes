# -*- coding: utf-8 -*-
# Copyright (C) 2018, eskerda <eskerda@gmail.com>
# Copyright (C) 2021, Altonss (https://github.com/Altonss)
# Copyright (C) 2022, eUgEntOptIc44 (https://github.com/eUgEntOptIc44)
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
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'DNT':'1',
            'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2',
            'Referer':'https://mynavega.emtmadrid.es/?locale=es'
        }
        scraper = scraper or PyBikesScraper()
        scraper_content = scraper.request(self.feed_url, method='POST', headers=headers)

        data = json.loads(scraper_content)

        data2 = json.loads(data['data'])

        self.stations = [BicimadStation(s) for s in data2['stations']]

class BicimadStation(BikeShareStation):
    def __init__(self, data):
        super(BicimadStation, self).__init__()
        self.name = data['name']
        self.longitude = float(data['longitude'])
        self.latitude = float(data['latitude'])
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
