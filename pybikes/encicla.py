# -*- coding: utf-8 -*-
# Copyright (C) 2015, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['Encicla', 'EnciclaStation']

class Encicla(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Encicla',
        'company': 'Sistema de Bicicletas Públicas del Valle de Aburrá'
    }

    def __init__(self, tag, feed_url, meta):
        super(Encicla, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
            
        stations = []
        
        data = json.loads(scraper.request(self.feed_url))
        for station in data['stations']:
            for item in station['items']:
                station = EnciclaStation(item)
                stations.append(station)
        self.stations = stations

class EnciclaStation(BikeShareStation):
    def __init__(self, item):
        super(EnciclaStation, self).__init__()
        '''
            {
            "order": 0,
            "name": "Moravia",
            "address": "CALLE 82A # 52-29",
            "description": "Frente a la entrada principal del Centro de Desarrollo Cultural de Moravia",
            "lat": "6.276585",
            "lon": "-75.564804",
            "type": "manual",
            "capacity": 15,
            "bikes": 8,
            "places": null,
            "picture": "http:\/\/encicla.gov.co\/wp-content\/uploads\/estaciones-360-moravia.jpg",
            "bikes_state": 0,
            "places_state": "danger",
            "closed": 0,
            "cdo": 0
            }
        '''
        self.name      = item['name']
        self.longitude = float(item['lon'])
        self.latitude  = float(item['lat'])
        self.bikes     = int(item['bikes'])
        places         = item['places']
        if not places:
            self.free = 0
        else:
            self.free  = int(places)
        # 'bikes_state' may also be a label as 'warning' as well, do not try to cast it to int
        # 'capacity' field may present a number which is smaller than the number of 'bikes',
        # it is not straightforward to know what it actually means. Consequently, it was not
        # included in the extras on the 'slots' field.
        self.extra = {
            'address': item['address'],
            'description': item['description'],
            'type': item['type'],
            'picture': item['picture'],
            'bikes_state': item['bikes_state'],
            'places_state': item['places_state'],
            'closed': int(item['closed']),
            'cdo': int(item['cdo'])
        }
