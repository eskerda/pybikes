# -*- coding: utf-8 -*-
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import re

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class BiciFerrolTerra(BikeShareSystem):
    def __init__(self, tag, meta, url):
        super(BiciFerrolTerra, self).__init__(tag, meta)
        self.url = url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        raw = scraper.request(self.url)

        # extract stations from js
        coords_raw = re.findall(r'new GMarker\([\s\S]*?\)(?:\s*;)', raw)
        # code is repeated, deduplicate
        station_coords = []
        for item in coords_raw:
            if item not in station_coords:
                station_coords.append(item)

        # getting station availability from tooltip listener
        station_availability = re.findall(r'GEvent.addListener\(marker_subguri[\s\S]*?\)(?:\s*;)', raw)

        stations = list(zip(station_coords, station_availability))
        self.stations = list(map(lambda i: BiciFerrolTerraStation(*i), stations))


class BiciFerrolTerraStation(BikeShareStation):
    def __init__(self, coords, availability):
        super(BiciFerrolTerraStation, self).__init__()
        self.name = re.search(r"title:'(.*?)'", coords).group(1)

        latitude, longitude = map(float, re.findall(r'-?\d+\.\d+', coords))
        self.latitude = latitude
        self.longitude = longitude

        self.bikes = int(re.search(r'Bicicletas dispo\xf1ibles: (-?\d+)', availability).group(1))
        self.free = int(re.search(r'Postos libres: (-?\d+)', availability).group(1))
        self.extra = {
            'slots': self.bikes + self.free,
            'schedule': re.search(r'Horario: ([^<]+)</', availability).group(1),
        }
