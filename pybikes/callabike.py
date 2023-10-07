# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) 2021, Altonss https://github.com/Altonss
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs

class Callabike(Gbfs):
    authed = True

    meta = {
        'system': 'callabike',
        'company': ['DB'],
    }

    def __init__(self, tag, meta, feed_url, key):
        super(Callabike, self).__init__(tag, meta, feed_url)
        self.key = key

    @staticmethod
    def authorize(scraper, key):
        request = scraper.request

        print(key)
        headers = {
            'DB-Client-Id': key['client_id'],
            'DB-Api-Key': key['client_secret'],
            'accept': "application/json"
        }

        def _request(*args, **kwargs):
            headers = kwargs.get('headers', {})
            kwargs['headers'] = headers
            return request(*args, **kwargs)

        scraper.request = _request

    @property
    def default_feeds(self):
        url = self.feed_url
        return {
            "station_information": 'https://apis.deutschebahn.com/db-api-marketplace/apis/shared-mobility-gbfs/2-2/de/CallABike/station_information',
            "station_status": 'https://apis.deutschebahn.com/db-api-marketplace/apis/shared-mobility-gbfs/2-2/de/CallABike/station_status',
        }

    def update(self, scraper=None):
        # Patch default scraper request method
        scraper = scraper or PyBikesScraper()
        Callabike.authorize(scraper, self.key)
        super(Callabike, self).update(scraper)
