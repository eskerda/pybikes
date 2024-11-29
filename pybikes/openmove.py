# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

FEED_URL = 'https://otp.opendatahub.com/otp/routers/openmove/bike_rental'


class OpenMove(BikeShareSystem):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    def __init__(self, tag, meta, network):
        super(OpenMove, self).__init__(tag, meta)
        self.network = network

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = scraper.request(FEED_URL,
                               headers=OpenMove.headers)
        data = json.loads(data)
        data = filter(lambda s: self.network in s['networks'], data['stations'])
        data = list(data)

        stations = []

        for station in data:
            if station['isFloatingBike']:
                continue
            stations.append(OpenMoveStation(station))

        self.stations = stations


class OpenMoveStation(BikeShareStation):
    def __init__(self, data):
        super(OpenMoveStation, self).__init__()
        self.name = data['name']
        self.latitude = float(data['y'])
        self.longitude = float(data['x'])

        self.bikes = int(data['bikesAvailable'])
        self.free = int(data['spacesAvailable'])

        self.extra = {
            'uid': data['id'].replace('"', ''),
            'last_update': data['lastReportedEpochSeconds'],
            'online': data['realTimeData'],
        }
