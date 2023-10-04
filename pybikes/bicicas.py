# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json
from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

FEED_URL = 'https://ws2.bicicas.es/bench_status_map'

class Bicicas(BikeShareSystem):
    sync = True
   
    def update(self, scraper = None):
        scraper = scraper or PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(FEED_URL))
        for item in data['features']:
            station = BicicasStation(item)
            stations.append(station)

        self.stations = stations

class BicicasStation(BikeShareStation):
    def __init__(self, item):
        super(BicicasStation, self).__init__()

        self.name = item['properties']['name']
        self.longitude = item['geometry']['coordinates'][0]
        self.latitude = item['geometry']['coordinates'][1]

        anchors = item['properties']['anchors']
        bikes = item['properties']['bikes_available']

        # no bikes and base has no incidents
        free = filter(lambda item: item.get('bicycle') is None and len(item.get('incidents')) == 0, anchors)

        self.bikes = bikes
        self.free = len(list(free))

        has_ebikes = list(filter(lambda item: item.get('is_electric'), anchors))
        ebikes = len(has_ebikes)

        self.extra = {
            'has_ebikes': any(has_ebikes),
            'ebikes': ebikes,
            'slots': len(list(anchors)),
            'last_seen': item['properties']['last_seen'],
            'number_loans': int(item['properties']['number_loans']),
            'incidents': item['properties']['incidents'],
            'online': item['properties']['online'],
        }
