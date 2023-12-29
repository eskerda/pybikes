# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import filter_bounds


class Joco(BikeShareSystem):
    def __init__(self, tag, meta, bbox, feed_url):
        super(Joco, self).__init__(tag, meta)

        self.bbox = bbox
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))

        stations = []

        for station in data:
            stations.append(JocoStation(station))

        if self.bbox:
            stations = list(filter_bounds(stations, None, self.bbox))

        self.stations = stations


class JocoStation(BikeShareStation):
    def __init__(self, data):
        self.name = data["name"]
        self.latitude = float(data["lat"])
        self.longitude = float(data["lng"])

        slots = int(data["totalcapacity"])
        bikes = int(data["availabilty"])

        self.bikes = bikes
        self.free = slots - bikes

        self.extra = {
            "uid": data["id"],
            'has_ebikes': True,
            "ebikes": bikes,
            "address": data["address"],
            "postal_code": data["postal"],
            "slots": slots
        }
