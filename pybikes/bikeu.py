# -*- coding: utf-8 -*-
# Copyright (C) 2015, thesebas <thesebas@thesebas.net>
# Distributed under the AGPL license, see LICENSE.txt
import re
import json

from lxml import html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.compat import urljoin

REGEX = "setConfig\('StationsData',(\[.*\])\);"

class Bikeu(BikeShareSystem):

    meta = {
        'system': 'Bike U',
        'company': ['Bike U Sp. z o.o.']
    }

    def __init__(self, tag, meta, url):
        super(Bikeu, self).__init__(tag, meta)
        self.url = url

    def parse_map(self, body):
        matched = re.search(REGEX, body)
        if not matched:
            return None
        markers = json.loads(matched.group(1))
        return markers

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        body = scraper.request(self.url)
        markers = self.parse_map(body)
        self.stations = list(map(BikeuStation, markers))


class BikeuStation(BikeShareStation):
    def __init__(self, info):
        super(BikeuStation, self).__init__()
        self.latitude = float(info['Latitude'])
        self.longitude = float(info['Longitude'])

        self.name = info['Name']
        self.bikes = int(info['TotalAvailableBikes'])
        self.free = int(info['TotalLocks']) - self.bikes
        self.extra = {
            'uid': info['id'],
        }
