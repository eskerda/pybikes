# -*- coding: utf-8 -*-
# Copyright (C) 2010-2023, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


api_root = "https://api.jcdecaux.com/vls/v3/"

endpoints = {
    'contracts': 'contracts?apiKey={api_key}',
    'stations' : 'stations?apiKey={api_key}&contract={contract}',
    'station'  : 'stations/{station_id}?contract={contract}&apiKey={api_key}'
}


class Cyclocity(Bounded, BikeShareSystem):

    sync = True

    authed = True

    meta = {
        'system': 'Cyclocity',
        'company': ['JCDecaux'],
        'license': {
            'name': 'Open Licence',
            'url': 'https://developer.jcdecaux.com/#/opendata/licence'
        },
        'source': 'https://developer.jcdecaux.com'
    }

    def __init__(self, tag, meta, contract, key, bbox=None):
        super(Cyclocity, self).__init__(tag, meta, bounds=bbox)
        self.contract = contract
        self.api_key = key
        self.stations_url = api_root + endpoints['stations'].format(
            api_key  = self.api_key,
            contract = contract
        )
        self.station_url = api_root + endpoints['station'].format(
            api_key = self.api_key,
            contract = contract,
            station_id = '{station_id}' )

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        data = json.loads(scraper.request(self.stations_url))

        assert isinstance(data, list)

        # a bit of an overkill hack to be exact about the system having ebikes
        has_ebikes = any(map(lambda s: s['totalStands']['availabilities']['electricalBikes'] > 0, data))

        stations = []
        for info in data:
            try:
                station = CyclocityStation(info, self.station_url, has_ebikes)
            except Exception:
                continue
            stations.append(station)
        self.stations = stations

    @staticmethod
    def get_contracts(api_key, scraper=None):
        scraper = scraper or PyBikesScraper()
        url = api_root + endpoints['contracts'].format(api_key = api_key)
        return json.loads(scraper.request(url))


class CyclocityStation(BikeShareStation):

    def __init__(self, jcd_data, station_url, has_ebikes=False):
        super(CyclocityStation, self).__init__()

        self.name      = jcd_data['name']
        self.latitude  = jcd_data['position']['latitude']
        self.longitude = jcd_data['position']['longitude']

        stands         = jcd_data['totalStands']
        available      = stands['availabilities']

        self.bikes     = available['bikes']
        self.free      = available['stands']

        self.extra = {
            'uid': jcd_data['number'],
            'address': jcd_data['address'],
            'status': jcd_data['status'],
            'banking': jcd_data['banking'],
            'bonus': jcd_data['bonus'],
            'last_update': jcd_data['lastUpdate'],
            'slots': stands['capacity'],
            'has_ebikes': has_ebikes,
        }

        if has_ebikes:
            self.extra['ebikes'] = available['electricalBikes']
            self.extra['normal_bikes'] = available['mechanicalBikes']

        self.url = station_url.format(station_id = jcd_data['number'])

        if self.latitude is None or self.longitude is None:
            raise Exception('An station needs a lat/lng to be defined!')
