# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) 2021, Altonss https://github.com/Altonss
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.utils import keys
from pybikes.gbfs import Gbfs

STATION_INFORMATION = '{feed_url}/station_information'
STATION_STATUS = '{feed_url}/station_status'


class Callabike(Gbfs):
    authed = True

    meta = {
        'system': 'callabike',
        'company': ['DB'],
    }

    def __init__(self, tag, meta, feed_url, key, bbox):
        super(Callabike, self).__init__(tag, meta, feed_url)
        self.bbox = bbox

    @property
    def station_information(self):
        return STATION_INFORMATION.format(feed_url=self.feed_url)

    @property
    def station_status(self):
        return STATION_STATUS.format(feed_url=self.feed_url)

    @staticmethod
    def authorize(scraper):
        request = scraper.request

        headers = {
            'DB-Client-Id': keys.client_id,
            'DB-Api-Key': keys.client_secret,
            'accept': "application/json"
        }

        def _request(*args, **kwargs):
            kwargs['headers'] = headers
            return request(*args, **kwargs)

        scraper.request = _request

    @property
    def default_feeds(self):
        return {
            "station_information": self.station_information,
            "station_status": self.station_status,
        }

    def update(self, scraper=None):
        # Patch default scraper request method
        scraper = scraper or PyBikesScraper()
        Callabike.authorize(scraper)
        super(Callabike, self).update(scraper)
