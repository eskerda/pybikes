# -*- coding: utf-8 -*-
# Copyright (C) 2010-2026, eskerda <eskerda@gmail.com>
# Copyright (C) 2022-2023, eUgEntOptIc44 (https://github.com/eUgEntOptIc44)
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.contrib import TSTCache
from pybikes.utils import Bounded
from pybikes.compat import resources


cantons = resources.files('pybikes')/'geojson/ch_cantons.json'
geojson = json.loads(cantons.read_bytes())

FEED_URL = "https://rest.publibike.ch/v1/public/all/stations"

# caches the feed for 60s
cache = TSTCache(delta=60)


class Publibike(Bounded, BikeShareSystem):
    sync = True
    unifeed = True  # all 'networks' (instances) share the same feed

    meta = {
        "system": "PubliBike",
        "company": ["PubliBike AG"],
        "source": "https://api.publibike.ch/v1/static/api.html",
    }

    def __init__(self, tag, meta, canton=None):
        canton = canton or []
        canton = [canton] if isinstance(canton, str) else canton
        bounds = [f['geometry'] for f in filter(lambda d: d["properties"]["NAME"] in canton, geojson["features"])]
        bounds = filter(None, bounds)
        super().__init__(tag, meta, mbounds=list(bounds))

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper(cache)
        raw = scraper.request(FEED_URL)
        data = json.loads(raw)

        stations = [
            * map(PublibikeStation, data["publibike"]["stations"]),
            * map(VelospotStation, data["velospot"]["responseData"]),
        ]

        self.stations = stations


class PublibikeStation(BikeShareStation):
    def __init__(self, station):
        super(PublibikeStation, self).__init__()

        self.name = station['name']
        self.latitude = float(station['latitude'])
        self.longitude = float(station['longitude'])
        self.extra = {
            'uid': station['id'],
            'address': station['address'],
            'zip': station['zip'],
            'city': station['city'],
            'slots': station['capacity'],
            'ebikes': 0,
        }
        for vehicle in station['vehicles']:
            if (vehicle['type']['id'] == 2):
                self.extra['ebikes'] += 1
        self.bikes = len(station['vehicles'])
        self.free = self.extra['slots'] - self.bikes


class VelospotStation(BikeShareStation):
    def __init__(self, data):
        super().__init__()

        self.name = data["station_name"]
        self.latitude = float(data["lat"])
        self.longitude = float(data["lng"])

        self.bikes = int(data["totalBike"])
        self.free = 0

        self.extra = {
            "uid": data["station_id"],
            "address": data["station_address"],
            "ebikes": int(data["totalElectricalBike"]),
            "normal_bikes": int(data["totalNonElectricalBike"]),
        }
