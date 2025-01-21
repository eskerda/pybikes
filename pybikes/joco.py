# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Joco(BikeShareSystem):
    def __init__(self, tag, meta, feed_url):
        super(Joco, self).__init__(tag, meta)

        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))

        stations = []

        for station in data:
            stations.append(JocoStation(station))

        self.stations = stations


class JocoStation(BikeShareStation):
    def __init__(self, data):
        super(JocoStation, self).__init__()

        self.name = data["name"]
        self.latitude = float(data["info"]["position"]["coordinates"][1])
        self.longitude = float(data["info"]["position"]["coordinates"][0])

        bikes = int(data["slots"]["withAvailableVehicle"])

        self.bikes = bikes
        self.free = int(data["slots"]["free"])

        self.extra = {
            "uid": data["id"],
            'has_ebikes': True,
            "ebikes": bikes,
            "address": data["info"]["address"],
            "slots": int(data["slots"]["total"]),
            'online': data["state"] == "OPEN",
        }
