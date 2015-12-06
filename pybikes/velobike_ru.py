# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class VelobikeRU(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Velobike RU',
        'company': 'ЗАО «СитиБайк»'
    }

    def __init__(self, tag, feed_url, meta):
        super(VelobikeRU, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        # Each station is
        #{
        #  "Address": "415 - \u0443\u043b. \u0421\u0443\u0449\u0451\u0432\u0441\u043a\u0438\u0439 \u0412\u0430\u043b, \u0434.2",
        #  "FreePlaces": 12,
        #  "Id": "0415",
        #  "IsLocked": true,
        #  "Position": {
        #    "Lat": 55.7914268,
        #    "Lon": 37.5905396
        # },
        # "TotalPlaces": 12
        #}
        for item in data['Items']:
            name = item['Address']
            latitude = float(item['Position']['Lat'])
            longitude = float(item['Position']['Lon'])
            bikes = int(item['TotalPlaces'])-int(item['FreePlaces'])
            free = int(item['FreePlaces'])
            extra = {
                'uid': item['Id'],
                'slots': int(item['TotalPlaces']),
                'address': item['Address'],
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
