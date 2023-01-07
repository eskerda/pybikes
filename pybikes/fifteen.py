# -*- coding: utf-8 -*-

import re
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class FifteenAPI(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Fifteen',
        'company': ['Fifteen SAS']
    }

    def __init__(self, tag, feed_url, meta):
        super(FifteenAPI, self).__init__(tag, meta)
        self.feed_url = feed_url


# Each station is formatted as:
# {
#   "id": "cecqdqutu70fusn3jor0",
#   "type": 2,
#   "product_type": 2,
#   "entity_type": 0,
#   "info": {
#     "bike_autonomy": 19600,
#     "number_of_bikes": 10,
#     "bike_state_of_charge": 69
#   },
#   "location": {
#     "type": "Point",
#     "coordinates": [
#       5.38209613,
#       43.24693037
#     ]
#   },
#   "label": "Lapin Blanc",
#   "parent_id": "ce4bhih2rcd13ifvqfr0",
#   "distance": 5607.314337868474
# }
# Extracted from :https://levelo.ampmetropole.fr/api/stations at Marseille, France


class LeVelo(FifteenAPI):
    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        response = json.loads(scraper.request(self.feed_url))
        stations = []

        if response["statusCode"] != 200:
            return stations

        data = response["data"]["stations"]
        for s in data:
            lat = float(s['location']['coordinates'][0])
            lng = float(s['location']['coordinates'][1])
            name = s['label']
            bikes = int(s['info']['number_of_bikes'])
            free = 10 - bikes

            # Since there is no limit on the number of bikes,
            # we set it to 0 if the station is full
            if free < 0:
                free = 0

            # bike_state_of_charge is not always present
            if 'bike_state_of_charge' in s['info']:
                bike_state_of_charge = int(s['info']['bike_state_of_charge'])
            else:
                bike_state_of_charge = 0
            extra = {
                'bike_state_of_charge': bike_state_of_charge,
                'bike_autonomy': int(s['info']['bike_autonomy']),
                'id': s['id'],
                'distance' : int(s['distance']),
            }
            station = BikeShareStation(name, lat, lng, bikes, free, extra)
            stations.append(station)

        self.stations = stations

class Vilvolt(FifteenAPI):
    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        data = json.loads(scraper.request(self.feed_url))
        stations = []

        for s in data:
            lat = float(s['location']['coordinates'][0])
            lng = float(s['location']['coordinates'][1])
            name = s['label']
            bikes = int(s['info']['number_of_bikes'])
            free = 10 - bikes

            # Since there is no limit on the number of bikes,
            # we set it to 0 if the station is full
            if free < 0:
                free = 0
            # bike_state_of_charge is not always present
            if 'bike_state_of_charge' in s['info']:
                bike_state_of_charge = int(s['info']['bike_state_of_charge'])
            else:
                bike_state_of_charge = 0
            extra = {
                'bike_state_of_charge': bike_state_of_charge,
                'bike_autonomy': int(s['info']['bike_autonomy']),
                'id': s['id'],
                'distance' : int(s['distance']),
            }
            station = BikeShareStation(name, lat, lng, bikes, free, extra)
            stations.append(station)

        self.stations = stations

class VeloBaie(FifteenAPI):

    info_url = "https://www.data.gouv.fr/fr/datasets/r/6aba2959-4200-4404-a707-b4954df29fb4"

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        info = json.loads(scraper.request(self.info_url))['data']['stations']
        status = json.loads(scraper.request(self.feed_url))['data']['stations']
        stations = []
        nb_stations = len(info)
        for i in range(nb_stations):
            if status[i]['is_installed'] == False:
                continue
            if info[i]['station_id'] != status[i]['station_id']:
                continue
            lat = float(info[i]['lat'])
            lng = float(info[i]['lon'])
            name = info[i]['name']
            bikes = int(status[i]['num_bikes_available'])
            free = int(status[i]['num_docks_available'])
            extra = {}
            station = BikeShareStation(name, lat, lng, bikes, free, extra)
            stations.append(station)

        self.stations = stations
