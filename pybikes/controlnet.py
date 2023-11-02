# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Controlnet(BikeShareSystem):

    def __init__(self, tag, feed_url, meta):
        super(Controlnet, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        res = json.loads(scraper.request(self.feed_url, method='GET'))
        stations = filter(lambda item: item.get('Borrado') == '0', res)
        self.stations = list(map(ControlnetStation, stations))


class ControlnetStation(BikeShareStation):
    def __init__(self, station):
        super(ControlnetStation, self).__init__()

        self.name = station['Nombre']

        # some coordinates are separated by commas, some are separated by dots
        # and at least one has the wrong sign
        self.latitude = -abs(float(station['Lat'].replace(',', '.')))
        self.longitude = -abs(float(station['Lon'].replace(',', '.')))

        self.bikes = station['CantidadOcupado']
        self.free = station['CantidadVacio']

        self.extra = {
            'uid': station['TotemId'],
            'online': not station['IsOffline'],
            'address': station['Direccion'],
            'station_type': 'manual' if station['TipoEstacion'] == 'M' else 'automatic',
            'slots': station['CantidadAnclajes'] or station['Capacidad']
        }
