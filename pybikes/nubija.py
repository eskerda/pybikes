# -*- coding: utf-8 -*-
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) 2025, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


ENDPOINT = "https://ar.nubija.com:55789/v1/station/list/user"


class Nubija(BikeShareSystem):
    authed = True

    def __init__(self, tag, meta, area, key):
        super(Nubija, self).__init__(tag, meta)
        self.area = area
        self.app_token = key[8:-8]

    @property
    def headers(self):
        return {
            "app-token": self.app_token,
            "user-agent": "okhttp/3.14.9",
        }

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        body = scraper.request(ENDPOINT, headers=self.headers)
        data = json.loads(body)

        stations = filter(lambda s: s["area"] == self.area, data["station"])

        self.stations = [
            BikeShareStation(
                name=s["station_cd"],
                latitude=float(s["x_pos"]),
                longitude=float(s["y_pos"]),
                bikes=0,
                free=int(s["parking_count"]),
                extra={
                    "uid": s["id"],
                    "number": int(s["tmno"]),
                    "address": s["address"],
                },
            )
            for s in stations
        ]
