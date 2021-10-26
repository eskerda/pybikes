# -*- coding: utf-8 -*-
# Copyright (C) 2021, Altonss https://github.com/Altonss
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

class Ecovelo(BikeShareSystem):
 
    meta = {
        'system': 'Ecovelo',
        'company': ['Ecovelo'],
    }

    BASE_URL = "https://api.cyclist.ecovelo.mobi/v2/stations?&program={dataset}&limit=100"

    def __init__(self, tag, dataset, meta):
        super(Ecovelo, self).__init__(tag, meta)
        self.feed_url = Ecovelo.BASE_URL.format(dataset=dataset)


    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))
        stations = map(lambda r: r, data['data'])
        self.stations = list(map(EcoveloStation, stations))
		

class EcoveloStation(BikeShareStation):
    def __init__(self, fields):
		name = fields['name']
		latitude = float(fields['position']['latitude'])
		longitude = float(fields['position']['longitude'])
		bikes = int(fields['docks']['total_vehicules'])
		free = int(fields['docks']['total_free'])
		extra = {
            'status': fields['status'],
            'uid': str(fields['id']),
            'online': fields['status'] == "open",
        }
		super(EcoveloStation, self).__init__(name, latitude, longitude, bikes, free, extra)
