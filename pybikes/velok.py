# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
import codecs

from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['VelokSystem', 'VelokStation']

parse_methods = {
    'json': 'get_json_stations'
}

class VelokSystem(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Velok'
    }

    def __init__(self, tag, feed_url, meta, format):
        super( VelokSystem, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.method = format

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        if self.method not in parse_methods:
            raise Exception(
                'Extractor for method %s is not implemented' % self.method )

        self.stations = eval(parse_methods[self.method])(self, scraper)

def get_json_stations(self, scraper):
    data = json.loads(scraper.request(self.feed_url))
    stations = []
    for marker in data['features']:
        try:
            station = VelokStation.from_json(marker)
        except (exceptions.StationPlannedException, exceptions.InvalidStation):
            continue
        
        stations.append(station)
    return stations


class VelokStation(BikeShareStation):
    def __init__(self):
        super(VelokStation, self).__init__()


    @staticmethod
    def from_json(data):
        '''
          {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [5.98276, 49.49473]
            },
            "properties": {
                "id": "velok:1",
                "open": true,
                "name": "Avenue de la Gare",
                "city": "Esch-sur-Alzette",
                "address": "Coin Rue de l’Alzette",
                "photo": "https://webservice.velok.lu/images/photos/1.jpg",
                "docks": 7,
                "available_bikes": 4,
                "available_ebikes": 0,
                "available_docks": 3,
                "last_update": null,
                "dock_status": [{
                    "status": "occupied",
                    "bikeType": "manual"
                }, {
                    "status": "free",
                    "bikeType": null
                }, {
                    "status": "occupied",
                    "bikeType": "manual"
                }, {
                    "status": "free",
                    "bikeType": null
                }, {
                    "status": "occupied",
                    "bikeType": "manual"
                }, {
                    "status": "free",
                    "bikeType": null
                }, {
                    "status": "occupied",
                    "bikeType": "manual"
                }]
            }
        }
        '''
        station = VelokStation()
        # if data['statusValue'] == 'Planned' or data['testStation']:
        #     raise exceptions.StationPlannedException()
        if data['properties']['id'].split(':')[0] != 'velok':
            raise exceptions.InvalidStation()

        station.name      = "%s" % (data['properties']['name'])
        station.longitude = float(data['geometry']['coordinates'][0])
        station.latitude  = float(data['geometry']['coordinates'][1])
        station.bikes     = int(data['properties']['available_bikes'])+ int(data['properties']['available_ebikes'])
        station.free      = int(data['properties']['available_docks'])

        station.extra = {
            'uid': int(data['properties']['id'].split(':')[1]),
            'address': data['properties']['address'],
            'city': data['properties']['city'],
            'photo': data['properties']['photo'],
            'totalDocks': data['properties']['docks'],
            'open':data['properties']['open']
        }

        return station
