# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


class Baksi(Bounded, BikeShareSystem):

    meta = {
        'system': 'Baksi',
        'company': ['Baksi Bike Sharing System']
    }

    def __init__(self, tag, meta, feed_url, bbox=None):
        super(Baksi, self).__init__(tag, meta, bounds=bbox)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        html_data = scraper.request(self.feed_url)
        ex_data = re.search(r'var all = (\[.*\]);', html_data).group(1)
        data = json.loads(ex_data)

        self.stations = list(map(BaksiStation, data))


class BaksiStation(BikeShareStation):
    def __init__(self, data):
        super(BaksiStation, self).__init__()

        uid, name = data[0].split('-', 1)

        self.name = name
        self.latitude = float(data[5])
        self.longitude = float(data[6])

        self.bikes = int(re.findall(r'\d+', data[2])[0])
        self.free = int(re.findall(r'\d+', data[3])[0])

        self.extra = {
            'uid': uid,
            'online': 'Aktif' in data[1],
        }
