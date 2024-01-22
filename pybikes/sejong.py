# -*- coding: utf-8 -*-
# Distributed under the LGPL license, see LICENSE.txt
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


class Sejong(Bounded, BikeShareSystem):
    def __init__(self, tag, meta, feed_url, bbox=None):
        super(Sejong, self).__init__(tag, meta, bounds=bbox)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations_data = json.loads(scraper.request(self.feed_url))

        stations = []
        for station_data in stations_data["data"]["sbike_station"]:
            station = SejongStation(station_data)
            stations.append(station)

        self.stations = stations


class SejongStation(BikeShareStation):
    def __init__(self, data):
        super(SejongStation, self).__init__()

        self.name = data["station_name"]
        self.latitude = float(data["y_pos"])
        self.longitude = float(data["x_pos"])

        self.bikes = int(data["bike_parking"])

        self.extra = {
            "uid": data["station_id"],
            "address": data["addr"]
        }
