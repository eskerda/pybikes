# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

FEED_URL = "https://gate.slovnaftbajk.sk/AppGate2.php"


class SlovnaftBajk(BikeShareSystem):
    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations = []

        data = json.loads(
            scraper.request(
                FEED_URL,
                method="POST",
                data=json.dumps({"Cmd": "GetAllStationInfo", "Area": "BA"}),
            )
        )

        # filter out test stations
        data = filter(lambda item: item.get("test_station") == "0", data["Info"])

        for station in data:
            station = SlovnaftBajkStation(station)
            stations.append(station)

        self.stations = stations


class SlovnaftBajkStation(BikeShareStation):
    def __init__(self, data):
        super(SlovnaftBajkStation, self).__init__()

        self.name = data["Name"]
        self.bikes = int(data["BikeNum"])
        self.free = int(data["DockNum"])

        self.latitude = float(data["GpsLat"])
        self.longitude = float(data["GpsLon"])

        self.extra = {
            "uid": data["Station"],
            "ebikes": int(data["eBikeNum"]),
            "online": data["active"] == "1",
        }
