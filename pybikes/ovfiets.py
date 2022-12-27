# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Copyright (C) 2022, eUgEntOptIc44 (https://github.com/eUgEntOptIc44)
# Distributed under the AGPL license, see LICENSE.txt

import json
import re

try:
    # Python 2
    from urlparse import urljoin
except ImportError:
    # Python 3
    from urllib.parse import urljoin

from pybikes import BikeShareSystem, BikeShareStation, exceptions
from pybikes.utils import PyBikesScraper
from pybikes.gbfs import GbfsStation
from pybikes.contrib import TSTCache

try:
    # Python 2
    unicode
except NameError:
    # Python 3
    unicode = str

__all__ = ['Ovfiets']

# cache the feed for 60s
cache = TSTCache(delta=60)

class Ovfiets(BikeShareSystem):
    sync = True
    unifeed = True # all OV fiets stations are served as one shared feed

    station_cls = None

    def __init__(
        self,
        tag,
        meta,
        region_codes,
        force_https=False,
        station_information=False,
        station_status=False
    ):
        super(Ovfiets, self).__init__(tag, meta)
        self.force_https = force_https

        self.region_codes = region_codes

        self.feeds = {
            "station_information": "https://gbfs.openov.nl/ovfiets/station_information.json",
            "station_status": "https://gbfs.openov.nl/ovfiets/station_status.json"
        }
        if station_information:
            self.feeds['station_information'] = station_information

        if station_status:
            self.feeds['station_status'] = station_status

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper(cache)

        feeds = self.feeds

        # Station Information and Station Status data retrieval
        station_information = json.loads(
            scraper.request(feeds['station_information'])
        )['data']['stations']
        station_status = json.loads(
            scraper.request(feeds['station_status'])
        )['data']['stations']
        
        # Aggregate status and information by uid
        # Note there's no guarantee that station_status has the same
        # station_ids as station_information.
        station_information = {s['station_id']: s for s in station_information}
        station_status = {s['station_id']: s for s in station_status}
        
        # Any station not in station_information will be ignored
        stations = [
            (station_information[uid], station_status[uid])
            for uid in station_information.keys()
        ]

        self.stations = []
        for info, status in stations:
            region_id = ''
            if 'region_id' in info:
                region_id = str(re.sub(r'[^A-Z]+','',str(info['region_id']).upper()))
            
            if region_id not in self.region_codes:
                continue
            
            info.update(status)
            try:
                station = self.station_cls(info)
            except exceptions.StationPlannedException:
                continue
            self.stations.append(station)

Ovfiets.station_cls = GbfsStation
