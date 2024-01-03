# -*- coding: utf-8 -*-
# Distributed under the LGPL license, see LICENSE.txt
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>

import json
import re

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Tashu(BikeShareSystem):
    def __init__(self, tag, meta, endpoint):
        super(Tashu, self).__init__(tag, meta)
        self.endpoint = endpoint

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        raw = scraper.request(self.endpoint)

        marker_var = re.search(r'var station_json = JSON.parse\(\'(.*)\'\);', raw)
        markers = json.loads(marker_var.group(1))

        stations = []
        for station_data in markers:
            station = TashuStation(station_data)
            stations.append(station)

        self.stations = stations


class TashuStation(BikeShareStation):
    def __init__(self, data):
        super(TashuStation, self).__init__()

        self.name = data["name"]
        self.latitude = float(data["x_pos"])
        self.longitude = float(data["y_pos"])

        self.bikes = int(data["parking_count"])

        self.extra = {
            "uid": data["id"],
            "address": data["address"],
        }
