# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['Velobike', 'VelobikeStation']

class Velobike(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Velobike',
        'company': 'Velobike.kz, LLP'
    }

    def __init__(self, tag, feed_url, meta):
        super(Velobike, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
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
        #     "address":"\u041d\u0430 \u043f\u0435\u0440\u0435\u0441\u0435\u0447\u0435\u043d\u0438\u0438 \u0443\u043b. \u0410\u043a\u043c\u0435\u0448\u0435\u0442\u044c, \u0443\u043b.\u041a\u0443\u043d\u0430\u0435\u0432\u0430.",
        #     "avl_bikes":1,
        #     "is_deleted":0,
        #     "is_sales":0,
        #     "is_not_active":0
        # }
        for item in data['data']:
            if item['is_sales'] == 1:
                continue
            name = item['name']
            latitude = item['lat']
            longitude = item['lng']
            bikes = item['avl_bikes']
            free = item['free_slots']
            extra = {
                'slots' : item['total_slots'],
                'address' : item['address'],
            }
            station = VelobikeStation(name, latitude, longitude,
                                    bikes, free, extra)
            stations.append(station)
        self.stations = stations

class VelobikeStation(BikeShareStation):
    def __init__(self, name, latitude, longitude, bikes, free, extra):
        super(VelobikeStation, self).__init__()

        self.name       = name
        self.latitude   = float(latitude)
        self.longitude  = float(longitude)
        self.bikes      = int(bikes)
        self.free       = int(free)
        self.extra      = extra
