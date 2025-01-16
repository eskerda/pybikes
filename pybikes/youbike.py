# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class YouBikeTw(BikeShareSystem):
    FEED_URL_V2 = "https://apis.youbike.com.tw/json/station-yb2.json"

    unifeed = True

    meta = {
        "system": "YouBike",
        "company": [
            "YouBike Co., Ltd.",
        ],
    }

    def __init__(self, tag, meta, uid):
        super(YouBikeTw, self).__init__(tag, meta)
        self.uid = uid

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.FEED_URL_V2))
        data = filter(
            lambda item: item.get("area_code") == self.uid
            and item.get("lat") != ""
            and item.get("lng") != "",
            data,
        )

        stations = []

        for item in data:
            station = YouBikeTwStation(item)
            stations.append(station)

        self.stations = stations


class YouBikeTwStation(BikeShareStation):
    def __init__(self, data):
        super(YouBikeTwStation, self).__init__()

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
            "normal_bikes": data["available_spaces_detail"]["yb1"] + data["available_spaces_detail"]["yb2"],
            "ebikes": data["available_spaces_detail"]["eyb"],
            "last_updated": data["updated_at"],
            "online": data["status"] == 1,
            "youbike_version": data["type"],
            "en": {
                "name": data["name_en"],
                "district": data["district_en"],
                "address": data["address_en"],
            },
        }


class YouBikeCn(BikeShareSystem):
    meta = {
        "system": "YouBike",
        "company": [
            "YouBike Co., Ltd.",
        ]
    }

    def __init__(self, tag, meta, feed_url):
        super(YouBikeCn, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))

        data = filter(
            lambda item: 
            item.get("lat") != "" and item.get("lng") != "",
            data["retVal"],
        )

        stations = []

        for item in data:
            station = YouBikeCnStation(item)
            stations.append(station)

        self.stations = stations


class YouBikeCnStation(BikeShareStation):
    def __init__(self, data):
        super(YouBikeCnStation, self).__init__()

        self.name = data["name_cn"]
        self.latitude = float(data["lat"])
        self.longitude = float(data["lng"])
        self.bikes = int(data["available_spaces"])
        self.free = int(data["empty_spaces"])

        self.extra = {
            "uid": data["station_no"],
            "district": data["district_cn"],
            "address": data["address_cn"],
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
