# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['Punpunbikeshare', 'PunpunbikeshareStation']

class Punpunbikeshare(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Punpunbikeshare',
        'company': 'Pun Pun Bangkok Bicycle Share'
    }

    def __init__(self, tag, feed_url, meta):
        super(Punpunbikeshare, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        # Each station is
        # {
        #     "stationId":"01",
        #     "stationName":"",
        #     "location":"Chamchuri Square",
        #     "lat":"13.73345498316396",
        #     "lng":"100.52908658981323",
        #     "status":"1",
        #     "bikeDockCount":"8",
        #     "bikeDocks":[{"dockId":"9","bikeId":"0000A24C20C4","status":"1"},{"dockId":"10","bikeId":"0000E2CF1FC4","status":"1"},
        #                  {"dockId":"11","bikeId":"000052B71FC4","status":"1"},{"dockId":"12","bikeId":"","status":"1"}]
        # }

        for item in data['stations']:
            name = item['stationName']
            latitude = item['lat']
            longitude = item['lng']

            bikes_counter = 0
            free_docks_counter = 0
            for bikeDocks in item['bikeDocks']:
                if bikeDocks['bikeId'] == "":
                    free_docks_counter += 1
                else:
                    bikes_counter += 1
            bikes = bikes_counter
            free = free_docks_counter
            extra = {
                    'slots' : item['bikeDockCount'],
                    'address' : item['location']
            }
            station = PunpunbikeshareStation(name, latitude, longitude,
                                             bikes, free, extra)
            stations.append(station)
            self.stations = stations

class PunpunbikeshareStation(BikeShareStation):
    def __init__(self, name, latitude, longitude, bikes, free, extra):
        super(PunpunbikeshareStation, self).__init__()

        self.name       = name
        self.latitude   = float(latitude)
        self.longitude  = float(longitude)
        self.bikes      = int(bikes)
        self.free       = int(free)
        self.extra      = extra
