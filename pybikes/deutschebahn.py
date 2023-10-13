# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs
from pybikes.contrib import TSTCache


FEED_URL = 'https://apis.deutschebahn.com/db-api-marketplace/apis/shared-mobility-gbfs/2-2/de/{provider}/gbfs'

# caches the feed for 60s
cache = TSTCache(delta=60)


class DB(Gbfs):
    authed = True

    # All networks within use the same data feed
    unifeed = True

    meta = {
        'company': ['Deutsche Bahn AG'],
        'system': 'deutschebahn',
    }

    def __init__(self, tag, meta, key, bbox, provider):
        self.key = key
        super(DB, self).__init__(
            tag,
            meta,
            FEED_URL.format(provider=provider),
            bbox=bbox,
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
        super(DB, self).update(scraper)


class Callabike(DB):
    # All networks within use the same data feed
    unifeed = True

    meta = {
        'name': 'Call-A-Bike',
    }

    provider = 'CallABike'


    def __init__(self, * args, ** kwargs):
        super(Callabike, self).__init__(* args, ** kwargs, provider=Callabike.provider)
