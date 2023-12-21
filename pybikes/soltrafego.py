# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

STATIONS_URL = (
    "https://bikesharing.soltrafego.pt/index.php/adminapi/dashboard_data/{uid}"
)


class Soltrafego(BikeShareSystem):
    meta = {"company": ["SOLTRÁFEGO, SA"], "system": "Soltrafego"}

    def __init__(self, tag, uid, meta):
        super(Soltrafego, self).__init__(tag, meta)
        self.uid = uid

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        stations_url = STATIONS_URL.format(uid=self.uid)
        data = json.loads(scraper.request(stations_url))

        stations = []
        for station_data in data["stations"]:
            station = SoltrafegoStation(station_data)
            stations.append(station)

        self.stations = stations


class SoltrafegoStation(BikeShareStation):
    def __init__(self, data):
        super(SoltrafegoStation, self).__init__()

        self.name = data["name"]
        self.latitude = float(data["lat"])
        self.longitude = float(data["lon"])

        self.bikes = int(data["online_docked"])
        self.free = int(data["online_free"])

        self.extra = {
            "uid": data["id"],
            "address": data["address"],
            "last_update": data["updated_on"],
            "slots": len(list(data["docks"])),
            "online": data["active"] == "1",
        }
