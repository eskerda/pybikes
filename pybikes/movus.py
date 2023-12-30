# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) 2023, Lluis Esquerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Movus(BikeShareSystem):
    sync = True

    meta = {
        "company": ['Movilidad Urbana Sostenible SLU'],
    }

    def __init__(self, tag, meta, feed_url, ebikes):
        super(Movus, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.ebikes = ebikes

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        raw = scraper.request(self.feed_url)

        marker_var = re.search(r'var misPuntos = \[(.*?)\];', raw, re.DOTALL)

        # transform to valid json by removing last trailing comma and adding brackets
        marker_var = '[' + re.sub(r',\s*$', '', marker_var.group(1)) + ']'
        markers = json.loads(marker_var)

        stations = []

        for name, lat, lng, _, info in markers:
            # Ignore test or invalid stations
            if not lat or not lng:
                continue

            stations.append(MovusStation(name, lat, lng, info, self.ebikes))

        self.stations = stations

class MovusStation(BikeShareStation):
    def __init__(self, name, lat, lng, info, has_ebikes):
        super(MovusStation, self).__init__()

        self.name = name
        self.latitude = float(lat)
        self.longitude = float(lng)

        # There's no availability info at the moment
        if 'Actualizandose' in info:
            self.bikes = 0
            return

        # fuck it, the html is invalid, so regex again
        if has_ebikes:
            rgx = r'mecánicas:\s(\d+).*eléctricas:\s(\d+).*libres:\s(\d+)'
            bikes, ebikes, free = re.search(rgx, info).groups()
            self.bikes = int(bikes) + int(ebikes)
            self.free = int(free)
            self.extra = {'ebikes': int(ebikes)}
        else:
            rgx = r'Totales=(\d+).*disponibles=(\d+).*libres=(-?\d+)'
            slots, bikes, free = re.search(rgx, info).groups()
            self.bikes = int(bikes)
            # this can come as negative so we clamp to zero
            self.free = max(int(free), 0)
            self.extra = {'slots': int(slots)}
