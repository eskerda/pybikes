# -*- coding: utf-8 -*-
# Copyright (C) 2025, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) 2026, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.base import Vehicle, VehicleTypes

STATIONS_URL = 'https://batumvelo.ge/api/client/public/parking'
VEHICLES_URL = 'https://batumvelo.ge/api/client/public/available'


class Batumvelo(BikeShareSystem):

    def update(self, scraper = None):
        scraper = scraper or PyBikesScraper()

        headers = {
            'Accept': 'application/json',
        }

        stations = scraper.request(STATIONS_URL, headers=headers)
        stations = json.loads(stations)
        self.stations = list(map(BatumveloStation, stations))

        vehicles = scraper.request(VEHICLES_URL, headers=headers)
        vehicles = json.loads(vehicles)
        self.vehicles = list(map(lambda v: BatumveloVehicle(v, self), vehicles))


class BatumveloStation(BikeShareStation):
    def __init__(self, item):
        super(BatumveloStation, self).__init__()

        self.name = item['name']
        self.longitude = item['lng']
        self.latitude = item['lat']

        self.bikes = 0
        self.free = 0

        self.extra = {
            'online': item['type'] == 'ALLOW',
        }


class BatumveloVehicle(Vehicle):
    def __init__(self, data, system):

        lat = float(data['lat'])
        lng = float(data['lng'])

        extra = {}

        kind = VehicleTypes.bicycle

        super().__init__(lat, lng, extra=extra, system=system, vehicle_type=kind)
