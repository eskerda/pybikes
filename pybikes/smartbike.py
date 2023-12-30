# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class SmartBike(BikeShareSystem):
    meta = {
        'system': 'SmartBike',
        'company': ['ClearChannel']
    }

    def __init__(self, tag, meta, endpoint):
        super(SmartBike, self).__init__(tag, meta)

        self.stations_url = endpoint + '/station_list.json'
        self.stations_status_url = endpoint + '/station_status_list.json'


    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations = json.loads(scraper.request(self.stations_url))
        statuses = json.loads(scraper.request(self.stations_status_url))

        self.stations = list(map(lambda z: SmartBikeStation(*z), zip(stations, statuses)))


class SmartBikeStation(BikeShareStation):
    def __init__(self, info, status):
        assert info['id'] == status['id'], "info and status are non consecutive, fix your code"

        name = info['name']
        latitude = float(info['location']['lat'])
        longitude = float(info['location']['lon'])
        bikes = int(status['availability']['bikes'])
        free = int(status['availability']['slots'])
        extra = {
            'status': status['status'],
            'uid': int(info['id']),
            'address': info['address'],
        }

        super(SmartBikeStation, self).__init__(name, latitude, longitude, bikes, free, extra)
