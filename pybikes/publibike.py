# -*- coding: utf-8 -*-
# Copyright (C) 2010-2022, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from .base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper, filter_bounds
from pybikes.contrib import TSTCache

__all__ = ['Publibike', 'PublibikeStation']

BASE_URL = 'https://{hostname}/v1/public/partner/stations'

# Since most networks share the same hostname, there's no need to keep hitting
# the endpoint on the same urls. This caches the feed for 60s
cache = TSTCache(delta=60)


class Publibike(BikeShareSystem):
    sync = True
    unifeed = True # all 'networks' (instances) share the same feed

    meta = {
        'system': 'PubliBike',
        'company': ['PubliBike AG']
    }

    def __init__(self, tag, meta, city_uid, hostname='api.publibike.ch',
                 bbox=None):
        super(Publibike, self).__init__(tag, meta)
        self.url = BASE_URL.format(hostname=hostname)
        self.uid = city_uid
        self.bbox = bbox

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper(cache)
        stations = json.loads(
            scraper.request(self.url).encode('utf-8')
        )

        assert "stations" in stations, "Failed to find any PubliBike stations"
            
        stations = stations['stations']

        # currently (Dezember 2022) there is no endpoint available to query only stations for 'city_uid'
        # so we need to filter the data
        stations = filter(lambda s: s['network']['id'] == self.uid, stations)

        if self.bbox:
            def getter(station):
                lat, lng = station['latitude'], station['longitude']
                return (float(lat), float(lng))
            stations = filter_bounds(stations, getter, self.bbox)

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
        if "capacity" in station:
            try:
                self.extra['slots'] = int(station['capacity'])
            except TypeError:
                self.extra['slots'] = 0

            if self.extra['slots'] > 0:
                self.free = self.extra['slots'] - self.bikes
