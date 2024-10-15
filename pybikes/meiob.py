# -*- coding: utf-8 -*-
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import re

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Meiob(BikeShareSystem):

    def __init__(self, tag, meta, endpoint):
        super(Meiob, self).__init__(tag, meta)

        self.endpoint = endpoint

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations = []
        raw = scraper.request(self.endpoint)
        data = zip(
            re.findall(r'stationlat\">(.*?)</div>', raw, re.DOTALL),
            re.findall(r'stationlon\">(.*?)</div>', raw, re.DOTALL),
            re.findall(r'pe-xxl-3\">\n\s+<h2>(.*?)</h2>', raw, re.DOTALL),
            re.findall(r'Bicicletas disponíveis</p>\n\s+<p class=\"mb-0 bike__available\">(.*?)</p>', raw, re.DOTALL),
            re.findall(r'Docas disponíveis</p>\n\s+<p class=\"mb-0 bike__available\">(.*?)</p>', raw, re.DOTALL),
            re.findall(r'<div class=\"w-100\">\n\s+<p class=\"mb-0 bike__distance__title text-center\">(.*?)</p>', raw, re.DOTALL),
            re.findall(r'</p>\n\s+<p class=\"mb-0 bike__distance__title text-center\">(.*?)</p>', raw, re.DOTALL)
        )

        for lat, lon, name, bikes, free, address, city in data:
            latitude = float(lat)
            longitude = float(lon)

            # usually name is on the second element but not always
            parsed_name = name.split(' - ')
            if len(parsed_name) == 2:
              name = parsed_name[1]
            else:
              name = parsed_name[0]

            bikes = int(bikes)
            free = int(free)

            extra = {
              'address': address,
              'city': city
            }

            station = MeiobStation(name, latitude, longitude, bikes, free, extra)
            stations.append(station)
        self.stations = stations

class MeiobStation(BikeShareStation):
    def __init__(self, name, latitude, longitude, bikes, free, extra):
        super(MeiobStation, self).__init__()

        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.bikes = bikes
        self.free = free
        self.extra = extra
