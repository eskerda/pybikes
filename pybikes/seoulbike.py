# -*- coding: utf-8 -*-
# Distributed under the LGPL license, see LICENSE.txt
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class SeoulBike(BikeShareSystem):
    def __init__(self, tag, meta, feed_url):
        super(SeoulBike, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations_data = json.loads(
            scraper.request(
                self.feed_url,
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data="stationGrpSeq=ALL",
            )
        )

        stations = []
        for station_data in stations_data["realtimeList"]:
            station = SeoulBikeStation(station_data)
            stations.append(station)

        self.stations = stations


class SeoulBikeStation(BikeShareStation):
    def __init__(self, data):
        super(SeoulBikeStation, self).__init__()

        self.name = data["stationName"]
        self.latitude = float(data["stationLatitude"])
        self.longitude = float(data["stationLongitude"])

        bikes = int(data["parkingQRBikeCnt"])

        # seoul has kid-sized bikes
        # https://english.seoul.go.kr/seoul-introduces-saessak-ttareungi-public-bikes-for-young-adults/
        kid_bikes = int(data["parkingELECBikeCnt"])
        slots = int(data["rackTotCnt"])

        self.bikes = bikes + kid_bikes

        # bikes can overflow the station: people leave bikes close if there is no room
        # we could have more bikes than slots: in that case show 0 spaces
        self.free = max(slots - self.bikes, 0)

        self.extra = {
            "kid_bikes": kid_bikes,
            "slots": slots,
            "uid": data["stationId"],
        }
