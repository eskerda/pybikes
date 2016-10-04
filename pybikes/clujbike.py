# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class Clujbike(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Clujbike',
        'company': ['Municipiul Cluj-Napoca']
    }

    def __init__(self, tag, feed_url, meta):
        super(Clujbike, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
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

        data = json.loads(
            scraper.request(self.feed_url, 'POST', post_data, None)
        )
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
            name = item['StationName']
            latitude = float(item['Latitude'])
            longitude = float(item['Longitude'])

            if float(latitude) == 0.0 or float(longitude) == 0.0:
                continue

            bikes = int(item['OcuppiedSpots'])
            free = int(item['EmptySpots'])
            status = 'offline' if item['StatusType'] == 'Offline' else 'online'
            extra = {
                'slots': item['MaximumNumberOfBikes'],
                'address': item['Address'],
                'status': status
            }
            station = BikeShareStation(name, latitude, longitude,
                                       bikes, free, extra)
            stations.append(station)

        self.stations = stations
