# -*- coding: utf-8 -*-
# Copyright (C) 2015, thesebas <thesebas@thesebas.net>
# Distributed under the AGPL license, see LICENSE.txt
import re
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Bikeu', 'BikeuStation']

REGEX = "var mapDataLocations = (\[.*\]);"

class Bikeu(BikeShareSystem):

    meta = {
        'system': 'Bike U',
        'company': 'Bike U Sp. z o.o.'
    }

    def __init__(self, tag, meta, url):
        super(Bikeu, self).__init__(tag, meta)
        self.url = url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        matched = re.search(REGEX,scraper.request(self.url))
        markers = json.loads(matched.group(1))

        self.stations = map(BikeuStation, markers)


class BikeuStation(BikeShareStation):
    def __init__(self, info):
        super(BikeuStation, self).__init__()
        self.latitude = float(info['Latitude'])
        self.longitude = float(info['Longitude'])

        self.name = info['LocalTitle']
        self.bikes = info['AvailableBikesCount']
        self.free = info['FreeLocksCount']
