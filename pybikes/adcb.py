# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class AdcbBikeshare(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Adbcbikeshare',
        'company': ['Cyacle Bicycle Rental LLC']
    }

    def __init__(self, tag, feed_url, meta):
        super(AdcbBikeshare, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        # Each station is
        # {
        #     "id":3,
        #     "s":"Yas Marina",
        #     "n":"Yas Marina",
        #     "st":1,"b":false,
        #     "su":false,
        #     "m":false,
        #     "lu":1452259533032,
        #     "lc":1452260047004,
        #     "bk":true,
        #     "bl":true,
        #     "la":24.465793,
        #     "lo":54.60961,
        #     "da":6,
        #     "dx":0,
        #     "ba":4,
        #     "bx":0
        # }
        for item in data['stations']:
            name = item['n']
            latitude = float(item['la'])
            longitude = float(item['lo'])
            bikes = int(item['ba'])
            free = int(item['da'])
            extra = {
                'status': 'online' if item['st'] == 1 else 'offline',
                'has_bike_keys': item['bk'] and item['bl'],
                'uid': str(item['id'])
            }
            station = BikeShareStation(name, latitude, longitude,
                                       bikes, free, extra)
            stations.append(station)

        self.stations = stations
