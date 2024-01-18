# -*- coding: utf-8 -*-

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


FEED_URL = "https://api.charteredbike.in/api/v1/stations/get-all-station"

REQ_ARGS = {
    "lat": 21.1940305,
    "long": 72.825347,
    "version": "1.9.2",
    "buildNumber": 283,
}

REQ_HEADERS = {
    "User-Agent": "okhttp/3.12.1",
    "Accept": "application/json, text/plain, */*",
}


class CharteredBike(Bounded, BikeShareSystem):
    unifeed = True

    meta = {
        "system": "Chartered Bike",
        "company": ['CHARTERED BIKE PRIVATE LIMITED'],
    }

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        data = scraper.request(FEED_URL, params=REQ_ARGS, headers=REQ_HEADERS)
        data = json.loads(data)

        assert data['status'] == 200

        self.stations = list(map(CharteredBikeStation, data['data']))


class CharteredBikeStation(BikeShareStation):

    def __init__(self, info):
        super(CharteredBikeStation, self).__init__()

        self.name = info['stationName']
        self.latitude = float(info['latitude'])
        self.longitude = float(info['longitude'])

        self.bikes = int(info['bikesAvailable'] or 0)
        self.free = int(info['freeRacks'])

        self.extra = {
            "uid": info['stationId'],
            "ebikes": int(info['ebikesAvailable'] or 0),
            "number": int(info['stationNumber']),
            "online": info['active'],
        }
