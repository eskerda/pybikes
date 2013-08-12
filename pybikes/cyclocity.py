# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from pyquery import PyQuery as pq

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Cyclocity','CyclocityStation']

api_root = "https://api.jcdecaux.com/vls/v1/"

endpoints = {
    'contracts': 'contracts?apiKey={api_key}',
    'stations' : 'stations?apiKey={api_key}&contract={contract}',
    'station'  : 'stations/{station_id}?contract={contract}&apiKey={api_key}'
}

class Cyclocity(BikeShareSystem):

    sync = True

    authed = True

    meta = {
        'system': 'Cyclocity',
        'company': 'JCDecaux',
        'license': {
            'name': 'Open Licence',
            'url': 'https://developer.jcdecaux.com/#/opendata/licence'
        },
        'source': 'https://developer.jcdecaux.com'
    }

    def __init__(self, tag, meta, contract, key):
        super( Cyclocity, self).__init__(tag, meta)
        self.contract = contract
        self.api_key = key
        self.stations_url = api_root + endpoints['stations'].format(
            api_key  = self.api_key,
            contract = contract
        )

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        data = json.loads(scraper.request(self.stations_url))
        stations = []
        for index, info in enumerate(data):
            station_url = api_root + endpoints['station'].format(
                api_key    = self.api_key,
                contract   = self.contract,
                station_id = "{station_id}"
            )
            station = CyclocityStation(index, info, station_url)
            stations.append(station)
        self.stations = stations

    @staticmethod
    def get_contracts(api_key, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        url = api_root + endpoints['contracts'].format(
            api_key = api_key
        )
        return json.loads(scraper.request(url))


class CyclocityStation(BikeShareStation):

    def __init__(self, id, jcd_data, station_url):
        super(CyclocityStation, self).__init__(id)

        self.name      = jcd_data['name']
        self.latitude  = jcd_data['position']['lat']
        self.longitude = jcd_data['position']['lng']
        self.bikes     = jcd_data['available_bikes']
        self.free      = jcd_data['available_bike_stands']

        self.extra = {
            'uid': jcd_data['number'],
            'address': jcd_data['address'],
            'status': jcd_data['status'],
            'banking': jcd_data['banking'],
            'bonus': jcd_data['bonus'],
            'last_update': jcd_data['last_update'],
            'slots': jcd_data['bike_stands']
        }

        self.url = station_url.format(station_id = jcd_data['number'])

    def update(self, scraper = None, net_update = False):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        super(CyclocityStation, self).update()
        if net_update:
            status = json.loads(scraper.request(self.url))
            self.__init__(self.id, status, self.url)
        return self