# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['Mvgmeinrad', 'MvgmeinradStation']

class Mvgmeinrad(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Mvgmeinrad',
        'company': ['Mainzer Verkehrsgesellschaft mbH (MVG)']
    }

    def __init__(self, tag, feed_url, meta):
        super(Mvgmeinrad, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        # Each station is
        # {
        #     "id":90,
        #     "name":"Hochheimer Stra\u00dfe",
        #     "blocked":false,
        #     "capacity":6,
        #     "docks_available":4,
        #     "bikes_available":2,
        #     "address":"Haltestelle Hochheimer Stra\u00dfe",
        #     "address_hint":"Haltestelle Hochheimer Stra\u00dfe",
        #     "latitude":"50.006479",
        #     "longitude":"8.288806",
        # }
        for item in data:
            name = item['name']
            latitude = item['latitude']
            longitude = item['longitude']
            bikes = item['bikes_available']
            free = item['docks_available']
            extra = {
                'slots' : item['capacity'],
                'address' : item['address']
            }
            station = MvgmeinradStation(name, latitude, longitude,
                                    bikes, free, extra)
            stations.append(station)
        self.stations = stations

class MvgmeinradStation(BikeShareStation):
    def __init__(self, name, latitude, longitude, bikes, free, extra):
        super(MvgmeinradStation, self).__init__()

        self.name       = name
        self.latitude   = float(latitude)
        self.longitude  = float(longitude)
        self.bikes      = int(bikes)
        self.free       = int(free)
        self.extra      = extra
