# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import re

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

BASE_URL = 'https://gestion.bicielx.es/mapa_prestamo.php'


class BiciElx(BikeShareSystem):
    sync = True

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        raw = scraper.request(BASE_URL)

        markers =  re.findall(r'var circle = .*?</div>"\)', raw, re.DOTALL)

        stations = []

        for marker in markers:
            stations.append(BiciElxStation(marker))

        self.stations = stations

class BiciElxStation(BikeShareStation):
    def __init__(self, data):
        super(BiciElxStation, self).__init__()

        self.name = re.search(r'\'>(.*?)</h2', data).group(1)

        coords = re.search(r'\[([^\]]+)\]', data).group(1)
        coords = coords.split(',')
        self.latitude = float(coords[0])
        self.longitude = float(coords[1])

        free, bikes = re.search(r'libres: (\d+).*disponibles: (\d+)', data).groups()
        self.bikes = int(bikes)
        self.free = int(free)

        uid = re.search(r'"([^"]+)"', data).group(1)
        self.extra = {'uid': int(uid)}
