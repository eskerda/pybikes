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
        'ebikes': True #This field is always present in the api, even there are no ebikes in the city, is this a problem?
    }

    BASE_URL = "https://api.cyclist.ecovelo.mobi/stations?&program={dataset}&limit=100"

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
        free = int(fields['statistics']['type']['available']['classic'] + int(fields['statistics']['vehicules']['type']['vae'])
        #should we add scooter?
        #free += int(fields['statistics']['vehicules']['type']['scooter'])
        extra = {
            'status': fields['status'],
            'uid': str(fields['id']),
            'online': fields['status'] == "open",
            'normal_bikes': int(fields['statistics']['vehicules']['available']['classic']),
            'ebikes': int(fields['statistics']['vehicules']['available']['vae']),
            #This field ('has_ebikes') is always present in the api, even there are no ebikes in the city, is this a problem?
            'has_ebikes': 'vae' in fields['statistics']['vehicules']['available']
        }
        super(EcoveloStation, self).__init__(name, latitude, longitude, bikes, free, extra)
