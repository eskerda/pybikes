# -*- coding: utf-8 -*-
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded
from pybikes.compat import resources


FEED_URL = "https://www.linkbike.my/linkbike_api/api_update_stationinfo.php"

geojson = json.loads(
    (resources.files('pybikes')/'geojson/penang.json').read_bytes()
)


class LinkBike(Bounded, BikeShareSystem):
    def __init__(self, tag, meta):
        super(LinkBike, self).__init__(tag, meta, bounds=geojson)


    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(FEED_URL))

        stations = []

        for station in data:
            stations.append(LinkBikeStation(station))

        self.stations = stations


class LinkBikeStation(BikeShareStation):
    def __init__(self, data):
        super(LinkBikeStation, self).__init__()

        self.name = data["name"]
        self.latitude = float(data["lat"])
        self.longitude = float(data["lng"])

        slots = int(data["capacity"])
        bikes = int(data["availbike"])
        self.bikes = bikes
        self.free = slots - bikes

        self.extra = {
            "uid": data["StId"],
            "slots": slots
        }
