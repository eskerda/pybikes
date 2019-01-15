# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
import codecs

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['GiraSystem', 'GiraStation']

class GiraSystem(BikeShareSystem):
    sync = True

    meta = {
        'system': 'Gira',
        'company': ['EMEL']
    }

    def __init__(self, tag, feed_url, meta, format):
        super( GiraSystem, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.method = format

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        self.stations = get_json_stations(self, scraper)

def get_json_stations(self, scraper):
    data = json.loads(scraper.request(self.feed_url))
    stations = []
    for marker in data['features']:
        try:
            station = GiraStation(marker)
        except exceptions.StationPlannedException:
            continue
        stations.append(station)
    return stations

class GiraStation(BikeShareStation):
    def __init__(self, info):
        super(GiraStation, self).__init__()
        
        if info['properties']['estado'] != 'active':
            raise exceptions.StationPlannedException()

        self.latitude = float(info['geometry']['coordinates'][0][1])
        self.longitude = float(info['geometry']['coordinates'][0][0])
        self.name = info['properties']['desig_comercial'].encode("utf-8")
        self.bikes = int(info['properties']['num_bicicletas'])
        self.free = int(info['properties']['num_docas']) - self.bikes
        self.extra = {'id_expl': info['properties']['id_expl'], 'id': info['id']}