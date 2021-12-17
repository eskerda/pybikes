# -*- coding: utf-8 -*-
# Copyright (C) 2021, Altonss https://github.com/Altonss
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

class Ecovelo(BikeShareSystem):

    meta = {
        'system': 'Ecovelo',
        'company': ['Ecovelo'],
        'ebikes': True #This field is always present in the api, even there are no ebikes in the city, is this a problem?
    }

    BASE_URL = "https://api.cyclist.ecovelo.mobi/stations"

    def __init__(self, tag, dataset, meta):
        super(Ecovelo, self).__init__(tag, meta)
        self.dataset = dataset

    def params(self, limit=100, after=None):
        return {
            "program": self.dataset,
            "limit": limit,
            "starting_after": after,
        }

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations = []
        params = self.params()

        while True:
            data = json.loads(scraper.request(Ecovelo.BASE_URL, params=params))
            stations += (d for d in data['data'] if d['object'] == 'station')

            if not data['has_more']:
                break

            params = self.params(after=data['data'][-1]['id'])

        self.stations = list(map(EcoveloStation, stations))


class EcoveloStation(BikeShareStation):
    def __init__(self, fields):
        name = fields['name']
        latitude = float(fields['position']['latitude'])
        longitude = float(fields['position']['longitude'])
        bikes = int(fields['docks']['total_vehicules'])
        free = int(fields['docks']['total_free'])
        types = fields['statistics']['vehicules']['type']
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
