# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['BCycleSystem', 'BCycleStation']

api_root = "https://publicapi.bcycle.com/api/1.0/"

endpoints = {
    'programs': 'ListPrograms',
    'stations': 'ListProgramKiosks/{program}'
}

class BCycleError(Exception):
    def __init__(self, msg):
            self.msg = msg

    def __repr__(self):
            return self.msg
    __str__ = __repr__


class BCycleSystem(BikeShareSystem):

    sync = True

    authed = True

    meta = { 
        'system': 'B-cycle',
        'company': [ 'Trek Bicycle Corporation'
                     ,'Humana'
                     ,'Crispin Porter + Bogusky' ]
    }

    def __init__(self, tag, meta, program, key):
        super( BCycleSystem, self).__init__(tag, meta)
        self.program = program
        self.api_key = key
        self.stations_url = api_root + endpoints['stations'].format(
            program = program
        )

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        scraper.headers['ApiKey'] = self.api_key
        data = json.loads(scraper.request(self.stations_url))
        stations = []
        for index, info in enumerate(data):
            try:
                station = BCycleStation(index)
                station.from_json(info)
                stations.append(station)
            except Exception:
                continue
        self.stations = stations

class BCycleStation(BikeShareStation):

    def from_json(self, data):
	if data['Status'] == 'ComingSoon':
		raise Exception('Station is coming soon')

        self.name      = "%s - %s" % (data['Id'], data['Name'])
        self.longitude = float(data['Location']['Latitude'])
        self.latitude  = float(data['Location']['Longitude'])
        self.bikes     = int(data['BikesAvailable'])
        self.free      = int(data['DocksAvailable'])

        self.extra = {
            'status': data['Status'],
            'street': data['Address']['Street'],
            'city': data['Address']['City'],
            'zipCode': data['Address']['ZipCode'],
        }

        return self

