# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) 2023, Lluis Esquerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Movus(BikeShareSystem):
    sync = True

    meta = {
        'company': ['Movilidad Urbana Sostenible SLU']
    }

    def __init__(self, tag, meta, feed_url):
        super(Movus, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        raw = scraper.request(self.feed_url)

        marker_var = re.search(r'var misPuntos = \[(.*?)\];', raw, re.DOTALL)
        markers = re.findall(r'\[(.*?)\],', marker_var.group(1), re.DOTALL)

        markers = map(lambda m: re.findall(r'\"(.*?)\"', m), markers)

        stations = []

        for name, lat, lng, _, info in markers:
            # Ignore test or invalid stations
            if not lat or not lng:
                continue

            stations.append(MovusStation(name, lat, lng, info))

        self.stations = stations

class MovusStation(BikeShareStation):
    def __init__(self, name, lat, lng, info):
        super(MovusStation, self).__init__()

        self.name = name
        self.latitude = float(lat)
        self.longitude = float(lng)

        # There's no availability info at the moment
        if 'Actualizandose' in info:
            self.bikes = 0
            return

        # fuck it, the html is invalid, so regex again
        rgx = r'Totales=(\d+).*disponibles=(\d+).*libres=(\d+)'

        slots, bikes, free = re.search(rgx, info).groups()

        self.bikes = int(bikes)
        self.free = int(free)

        self.extra = {'slots': int(slots)}
