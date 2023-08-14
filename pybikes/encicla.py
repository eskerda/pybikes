# -*- coding: utf-8 -*-
# Copyright (C) 2015, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Copyright (C) 2023, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json


from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


FEED_URL = 'https://webapp.metropol.gov.co/wsencicla/api/Disponibilidad/GetDisponibilidadMapas'


class Encicla(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Encicla',
        'company': ['Sistema de Bicicletas Públicas del Valle de Aburrá']
    }

    def update(self, scraper = None):
        scraper = scraper or PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(FEED_URL))
        for item in data:
            # discard 'Centro de Operaciones' (Operation Center) from the set of stations
            if int(item['cdo']) != 0:
                continue
            station = EnciclaStation(item)
            stations.append(station)

        self.stations = stations

class EnciclaStation(BikeShareStation):
    def __init__(self, item):
        super(EnciclaStation, self).__init__()

        self.name      = item['name']
        self.longitude = item['lon']
        self.latitude  = item['lat']

        # `places` is always 0.
        # Website shows places based on `capacity - bikes`
        bikes = item['bikes']
        slots = item['capacity']
        self.bikes = bikes
        self.free = slots - bikes

        self.extra = {
            'uid': item['id'],
            'slots': slots,
            'address': item['address'].strip(),
            'description': item['description'],
            'online': item['closed'] == '0',
        }
