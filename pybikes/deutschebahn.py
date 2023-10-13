# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) 2023, Lluis Esquerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes import PyBikesScraper
from pybikes.gbfs import Gbfs
from pybikes.contrib import TSTCache


FEED_URL = 'https://apis.deutschebahn.com/db-api-marketplace/apis/shared-mobility-gbfs/2-2/de/{provider}/gbfs'


class DB(Gbfs):
    authed = True

    cache = True
    cache_deltas = {
        # 12 hours
        'gbfs': 12 * 60 * 60,
        # 1 hour
        'station_information': 60 * 60,
        # 60 seconds
        'station_status': 60,
        # 12 hours
        'vehicle_types': 12 * 60 * 60,
    }

    meta = {
        'company': ['Deutsche Bahn AG'],
        'system': 'deutschebahn',
    }

    def __init__(self, tag, meta, key, provider, bbox=None):
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
        scraper = scraper or PyBikesScraper()
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
        super(Callabike, self).__init__(* args, provider=Callabike.provider, ** kwargs)
