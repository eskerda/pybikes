# -*- coding: utf-8 -*-
# Copyright (C) 2019, Louis Turpinat <turpinat.louis@gmail.com>
# Copyright (C) 2016, Lluis Esquerda <eskerda@gmail.com>
# Copyright (C) 2015, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


# Each station is formatted as:
# newmark_01(
#    28,
#    45.770958,
#    3.073871,
#    "<div class=\"mapbal\" align=\"left\">022 Jaurès<br>Vélos disponibles: 4
#    <br>Emplacements libres: 10<br>CB: Non<br></div>"
# );

# station_uid, latitude, longitude
STATIONS_RGX = r'newmark_\d+\(\s*(\d+)\s*,\s*(\d+.\d+),\s*(\d+.\d+)\s*,\s*\"{}\"'  # NOQA
# name, available_bikes, free_bike_stands, credit_card_enabled
STATUS_RGX = r'<div.*?>(.*?)<br>.*?:\s*(.*?)<br>.*?:\s*(.*?)<br>.*?:\s*(.*?)<br></div>'  # NOQA
DATA_RGX = STATIONS_RGX.format(STATUS_RGX)


class Smoove(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Smoove',
        'company': ['Smoove']
    }

    def __init__(self, tag, feed_url, meta):
        super(Smoove, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        html = scraper.request(self.feed_url, default_encoding='ISO-8859-1')
        stations_data = re.findall(DATA_RGX, html)
        stations = []
        # discards the last element of stations_data
        # which indicates if the station is credit card-enabled
        for uid, latitude, longitude, name, bikes, free, _ in stations_data:
            extra = {
                'uid': int(uid)
            }
            station = BikeShareStation(name, float(latitude), float(longitude),
                                       int(bikes), int(free), extra)
            stations.append(station)
        self.stations = stations


class SmooveAPI(Smoove):
    # Example feed:
    # https://helsinki-fi-smoove.klervi.net/api-public/stations
    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        data = json.loads(scraper.request(self.feed_url))
        stations = []
        for s in data['result']:
            # inoperative stations have 'coordinates': '', skip them
            if s['coordinates'] == '':
                continue
            lat, lng = map(float, s['coordinates'].split(','))
            name = s['name']
            bikes = int(s['avl_bikes'])
            free = int(s['free_slots'])
            total = int(s['total_slots'])
            status = 'online' if s['operative'] else 'offline'
            extra = {
                'slots': total,
                'status': status,
                'bank_card': s['style'] == 'CB',
            }
            idx = next(iter(re.findall(r'^(\w+\d+)\s+', name)), None)
            if idx:
                extra['uid'] = idx

            station = BikeShareStation(name, lat, lng, bikes, free, extra)
            stations.append(station)

        self.stations = stations


# Each station is formatted as:
# {
#   "name": "001 Jaude",
#   "nid": "1915",
#   "coordinates": [
#       "45.777457",
#       "3.081310"
#   ],
#   "total_slots": 24,
#   "free_slots": 22,
#   "avl_bikes": 0,
#   "operative": 200,
#   "style": "",
#   "favorite": false,
#   "sticky": false,
#   "type": "station"
# }
# Extracted from : https://www.c-velo.fr/api/getStations at Clermont-Ferrand, France


class CVeloSmoove(Smoove):    
    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        data = json.loads(scraper.request(self.feed_url))
        stations = []

        for s in data['response']:
            if s['coordinates'] == '':
                continue
            lat = float(s['coordinates'][0])
            lng = float(s['coordinates'][1])
            name = s['name']
            bikes = int(s['avl_bikes'])
            free = int(s['free_slots'])
            total = int(s['total_slots'])
            status = 'online' if s['operative'] else 'offline'
            extra = {
                'slots': total,
                'status': status,
                'bank_card': s['style'] == 'CB',
            }
            idx = next(iter(re.findall(r'^(\w+\d+)\s+', name)), None)
            if idx:
                extra['uid'] = idx

            station = BikeShareStation(name, lat, lng, bikes, free, extra)
            stations.append(station)

        self.stations = stations