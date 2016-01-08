# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['Clujbike', 'ClujbikeStation']

class Clujbike(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Clujbike',
        'company': 'Municipiul Cluj-Napoca'
    }

    def __init__(self, tag, feed_url, meta):
        super(Clujbike, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        post_data = {
            'sort' : '',
            'group' : '',
            'filter' : '',
            'StationName' : '',
            'Address' : '',
            'OcuppiedSpots' : '0',
            'EmptySpots' : '0',
            'MaximumNumberOfBikes' : '0',
            'LastSyncDate' : '',
            'IdStatus' : '0',
            'Status' : '',
            'StatusType' : '',
            'Latitude' : '0',
            'Longitude' : '0',
            'IsValid' : 'true',
            'CustomIsValid' : 'false',
            'Id' : '0',
        }

        data = json.loads(scraper.request(self.feed_url, 'POST', post_data, None))
        # Each station is
        # {
        #     "StationName":"Biblioteca Centrala",
        #     "Address":"Biblioteca Județeană Octavian Goga",
        #     "OcuppiedSpots":0,
        #     "EmptySpots":20,
        #     "MaximumNumberOfBikes":20,
        #     "LastSyncDate":"01/08/2016 12:26",
        #     "IdStatus":1,
        #     "Status":"Functional",
        #     "StatusType":"Subpopulated",
        #     "Latitude":46.777037,
        #     "Longitude":23.615109,
        #     "IsValid":true,
        #     "CustomIsValid":false,
        #     "Notifies":[],
        #     "Id":85,
        # }
        for item in data['Data']:
            if item['StatusType'] == 'Offline':
                continue
            name = item['StationName']
            latitude = item['Latitude']
            longitude = item['Longitude']
            bikes = item['OcuppiedSpots']
            free = item['EmptySpots']
            extra = {
                'slots' : item['MaximumNumberOfBikes'],
                'address' : item['Address'],
                'statustype' : item['StatusType']
            }
            station = ClujbikeStation(name, latitude, longitude,
                                      bikes, free, extra)
            stations.append(station)

        self.stations = stations

class ClujbikeStation(BikeShareStation):
    def __init__(self, name, latitude, longitude, bikes, free, extra):
        super(ClujbikeStation, self).__init__()

        self.name       = name
        self.latitude   = float(latitude)
        self.longitude  = float(longitude)
        self.bikes      = int(bikes)
        self.free       = int(free)
        self.extra      = extra
