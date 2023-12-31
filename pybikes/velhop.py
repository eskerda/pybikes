# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Velhop(BikeShareSystem):

    def __init__(self, tag, meta, feed_url):
        super(Velhop, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))

        stations = []

        for station in data:
            # ignore stations that haven't been installed
            if station["is_installed"] == 0:
                continue
            stations.append(VelhopStation(station))

        self.stations = stations


class VelhopStation(BikeShareStation):
    def __init__(self, data):
        super(VelhopStation, self).__init__()

        self.name = data["na"]
        self.latitude = float(data["coordonnees"]["lat"])
        self.longitude = float(data["coordonnees"]["lon"])

        self.bikes = int(data["av"])
        self.free = int(data["fr"])

        renting = int(data['is_renting']) == 1
        returning = int(data['is_returning']) == 1

        self.extra = {
            "uid": data["id"],
            "slots": int(data["to"]),
            'renting': renting,
            'returning': returning,
            "online": renting and returning,
            "last_update": data["last_reported"],
        }
