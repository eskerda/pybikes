# -*- coding: utf-8 -*-
# Copyright (C) 2010-2022, eskerda <eskerda@gmail.com>
# Copyright (C) 2022-2023, eUgEntOptIc44 (https://github.com/eUgEntOptIc44)
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper
from pybikes.contrib import TSTCache

__all__ = ['Publibike', 'PublibikeStation']

BASE_URL = 'https://{hostname}/v1/public/partner/stations'

# caches the feed for 60s
cache = TSTCache(delta=60)


class Publibike(BikeShareSystem):
    sync = True
    unifeed = True  # all 'networks' (instances) share the same feed

    meta = {
        'system': 'PubliBike',
        'company': ['PubliBike AG'],
        'source': 'https://api.publibike.ch/v1/static/api.html'
    }

    def __init__(self, tag, meta, city_uid, hostname='api.publibike.ch'):
        super(Publibike, self).__init__(tag, meta)
        self.url = BASE_URL.format(hostname=hostname)
        self.uid = city_uid

    def update(self, scraper=None):
        if scraper is None:
            # use cached feed if possible
            scraper = PyBikesScraper(cache)

        stations = json.loads(
            scraper.request(self.url).encode('utf-8')
        )

        assert "stations" in stations, "Failed to find any PubliBike stations"

        stations = stations['stations']

        # currently (Dezember 2022) there is no endpoint available
        # to query only stations for 'city_uid'
        # so we need to filter the data
        stations = filter(lambda s: s['network']['id'] == self.uid, stations)

        self.stations = list(map(PublibikeStation, stations))


class PublibikeStation(BikeShareStation):
    def __init__(self, station):
        super(PublibikeStation, self).__init__()

        self.name = station['name']
        self.latitude = float(station['latitude'])
        self.longitude = float(station['longitude'])
        self.extra = {}

        self.extra['uid'] = station['id']

        if 'address' in station:
            self.extra['address'] = station['address']

        if 'zip' in station:
            self.extra['zip'] = station['zip']

        if 'city' in station:
            self.extra['city'] = station['city']

        self.bikes = 0
        if "vehicles" in station:
            self.bikes = len(station['vehicles'])

        self.free = None
        try:
            self.extra['slots'] = station['capacity']
        except TypeError:
            self.extra['slots'] = 0

        if self.extra['slots'] > 0:
            self.free = self.extra['slots'] - self.bikes
