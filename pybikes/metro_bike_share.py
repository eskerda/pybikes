# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

class MetroBikeShare(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Metro Bike Share',
        'company': ['Los Angeles County Metropolitan Transportation Authority (Metro)', 'Bicycle Transit Systems Inc', 'B-cycle'],
    }

    def __init__(self, tag, feed_url, meta):
        super(MetroBikeShare, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
            scraper.ssl_verification = False

        data = json.loads(scraper.request(self.feed_url))

        # Each station is
        # {
        #   "geometry":{"coordinates":[-118.25905,34.04855],"type":"Point"},
        #   "properties":{
        #       "addressStreet":"723 Flower Street",
        #       "addressCity":"Los Angeles",
        #       "addressState":"CA",
        #       "addressZipCode":"90017",
        #       "bikesAvailable":16,
        #       "closeTime":"23:58:00",
        #       "docksAvailable":11,
        #       "eventEnd":null,
        #       "eventStart":null,
        #       "isEventBased":false,
        #       "isVirtual":false,
        #       "kioskId":3005,
        #       "kioskPublicStatus":"Active",
        #       "name":"Flower & 7th",
        #       "openTime":"00:02:00",
        #       "publicText":"",
        #       "timeZone":"Pacific Standard Time",
        #       "totalDocks":27,
        #       "trikesAvailable":0
        #   },
        #   "type":"Feature"}
        # }

        stations = []

        for item in data['features']:
            name = item['properties']['name']
            latitude = float(item['geometry']['coordinates'][1])
            longitude = float(item['geometry']['coordinates'][0])
            bikes = int(item['properties']['bikesAvailable'])
            free = int(item['properties']['docksAvailable'])
            extra = {
                'slots': int(item['properties']['totalDocks']),
                'address': item['properties']['addressStreet'],
                'uid' : item['properties']['kioskId'],
                'openTime' : item['properties']['openTime'],
                'closeTime' : item['properties']['closeTime'],
                'addressZipCode' : item['properties']['addressZipCode']
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)

        self.stations = stations
