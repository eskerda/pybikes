# -*- coding: utf-8 -*-
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import re
import lxml.html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Nubija(BikeShareSystem):
    def __init__(self, tag, meta, endpoint):
        super(Nubija, self).__init__(tag, meta)
        self.endpoint = endpoint

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        # data comes in html table format
        raw = scraper.request(self.endpoint)
        html = lxml.html.fromstring(raw)
        station_data = html.xpath('//table/tbody/tr')

        stations = []

        for station in station_data:
            stations.append(NubijaStation(station))

        self.stations = stations


class NubijaStation(BikeShareStation):
    def __init__(self, data):
        super(NubijaStation, self).__init__()

        self.name = data.xpath('.//td/div/span[@class="item-text"]/text()')[0]

        # extract coords from inline js
        coords = data.xpath('.//td[@class="view"]/a[@href]/@href')[0]
        latitude, longitude = re.findall(r'\d+\.\d+', coords)
        self.latitude = float(latitude)
        self.longitude = float(longitude)

        self.bikes = 0
        self.free = int(data.xpath('.//td[@class="count"]/text()')[0])

        self.extra = {
            "uid": data.xpath('.//td/div/span[@class="item-icon3"]/text()')[0],
            "area": data.xpath('.//td[@class="area"]/text()')[0]
        }
