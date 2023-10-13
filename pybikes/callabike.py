# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs
from pybikes.contrib import TSTCache


FEED_URL = 'https://apis.deutschebahn.com/db-api-marketplace/apis/shared-mobility-gbfs/2-2/de/CallABike'
STATION_INFORMATION = FEED_URL + '/station_information'
STATION_STATUS = FEED_URL + '/station_status'

# caches the feed for 60s
cache = TSTCache(delta=60)


class Callabike(Gbfs):
    authed = True

    # All networks within use the same data feed
    unifeed = True

    meta = {
        'name': 'Call-A-Bike',
        'system': 'callabike',
        'company': ['Deutsche Bahn AG'],
    }

    def __init__(self, tag, meta, key, bbox):
        self.key = key
        super(Callabike, self).__init__(
            tag,
            meta,
            FEED_URL,
            bbox=bbox,
            station_information=STATION_INFORMATION,
            station_status=STATION_STATUS
        )

    @property
    def auth_headers(self):
        return {
            'DB-Client-Id': self.key['client_id'],
            'DB-Api-Key': self.key['client_secret'],
            'accept': 'application/json',
        }

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper(cache)
        scraper.headers.update(self.auth_headers)
        super(Callabike, self).update(scraper)
