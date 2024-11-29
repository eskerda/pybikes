# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


FEED_URL = 'https://opendata.agglo-larochelle.fr/d4c/api/records/2.0/downloadfile/format=json&resource_id=1f124bea-d55f-457f-9eab-b7877d803435'


class YeloVelo(Bounded, BikeShareSystem):
    def __init__(self, tag, meta, bbox=None):
        super(YeloVelo, self).__init__(tag, meta, bounds=bbox)

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()

        stations_data = json.loads(scraper.request(FEED_URL))

        stations = []
        for station_data in stations_data:
            station = YeloVeloStation(station_data)
            stations.append(station)

        self.stations = stations


class YeloVeloStation(BikeShareStation):
    def __init__(self, data):
        super(YeloVeloStation, self).__init__()

        station_data = data['fields']

        self.name = station_data['station_nom']
        self.latitude = station_data['station_latitude']
        self.longitude = station_data['station_longitude']
        self.bikes = int(station_data['velos_disponibles'])
        self.free = int(station_data['accroches_libres'])
        self.extra = {
            'slots': station_data['nombre_emplacements'],
        }
