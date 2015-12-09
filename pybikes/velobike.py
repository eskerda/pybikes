# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class Velobike(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Velobike',
        'company': ['Velobike.kz, LLP', 'Smoove']
    }

    def __init__(self, tag, feed_url, meta):
        super(Velobike, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        # Each station is
        # {
        #     "id":41,
        #     "code":"036",
        #     "name":" Hotel \"Diplomat\" ",
        #     "lat":"51.130769",
        #     "lng":"71.429361",
        #     "photo":null,
        #     "desc":"",
        #     "total_slots":8,
        #     "free_slots":7,
        #     "address":"\u041d\u0430 ...",
        #     "avl_bikes":1,
        #     "is_deleted":0,
        #     "is_sales":0,
        #     "is_not_active":0
        # }
        for item in data['data']:
            if item['is_sales'] == 1:
                continue
            name = item['name']
            latitude = float(item['lat'])
            longitude = float(item['lng'])
            bikes = int(item['avl_bikes'])
            free = int(item['free_slots'])
            extra = {
                'uid': item['id'],
                'slots': int(item['total_slots']),
                'address': item['address'],
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
