# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

FEED_URL_V1 = "https://apis.youbike.com.tw/json/station-yb1.json"
FEED_URL_V2 = "https://apis.youbike.com.tw/json/station-yb2.json"


class YouBike(BikeShareSystem):
    unifeed = True

    meta = {
        "system": "YouBike",
        "company": [
            "YouBike Co., Ltd.",
        ],
    }

    def __init__(self, tag, meta, uid):
        super(YouBike, self).__init__(tag, meta)
        self.uid = uid

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        v1 = json.loads(scraper.request(FEED_URL_V1))
        v2 = json.loads(scraper.request(FEED_URL_V2))

        data = v1 + v2
        data = filter(
            lambda item: item.get("area_code") == self.uid
            and item.get("lat") != ""
            and item.get("lng") != "",
            data,
        )

        stations = []

        for item in data:
            station = YouBikeStation(item)
            stations.append(station)

        self.stations = stations


class YouBikeStation(BikeShareStation):
    def __init__(self, data):
        super(YouBikeStation, self).__init__()

        self.name = data["name_tw"]
        self.latitude = float(data["lat"])
        self.longitude = float(data["lng"])
        self.bikes = int(data["available_spaces"])
        self.free = int(data["empty_spaces"])

        self.extra = {
            "uid": data["station_no"],
            "district": data["district_tw"],
            "address": data["address_tw"],
            "slots": data["parking_spaces"],
            "last_updated": data["updated_at"],
            "online": data["status"] == 1,
            "youbike_version": data["type"],
            "en": {
                "name": data["name_en"],
                "district": data["district_en"],
                "address": data["address_en"],
            },
        }
