# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class Punpunbikeshare(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Smart Bike',
        'company': ['BTS Group Holdings'],
    }

    def __init__(self, tag, feed_url, meta):
        super(Punpunbikeshare, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        data = json.loads(scraper.request(self.feed_url))

        # Each station is like follows
        # If there's no bikeId in bikeDocks object, it means dock is free
        # Status seem mostly ignored by website, so let's not make assumptions
        # on that.
        # {
        #     "stationId":"01",
        #     "stationName":"foo bar",
        #     "location":"Chamchuri Square",
        #     "lat":"13.73345498316396",
        #     "lng":"100.52908658981323",
        #     "status":"1",
        #     "bikeDockCount":"8",
        #     "bikeDocks":[
        #         {"dockId":"9","bikeId":"0000A24C20C4","status":"1"},
        #         {"dockId":"10","bikeId":"0000E2CF1FC4","status":"1"},
        #         {"dockId":"11","bikeId":"000052B71FC4","status":"1"},
        #         {"dockId":"12","bikeId":"","status":"1"}
        #         ...
        #     ]
        # }

        stations = []

        for item in data['stations']:
            name = item['stationName']
            latitude = float(item['lat'])
            longitude = float(item['lng'])
            total_slots = int(item['bikeDockCount'])
            bike_uids = [b['bikeId'] for b in item['bikeDocks'] if b['bikeId']]
            bikes = len(bike_uids)
            free = total_slots - bikes
            extra = {
                'slots': total_slots,
                'address': item['location'],
                'uid': item['stationId'],
                'bike_uids': bike_uids,
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)

        self.stations = stations
