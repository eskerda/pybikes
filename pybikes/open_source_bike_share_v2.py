# -*- coding: utf-8 -*-
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import utils
from pybikes.open_source_bike_share import OpenSourceBikeShare


class OpenSourceBikeShareV2(OpenSourceBikeShare):
    authed = True

    def __init__(self, tag, meta, feed_url, key):
        super().__init__(tag, meta, feed_url)
        self.key = key

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()
        scraper.parse_cookies = False
        scraper.headers.update({
            'Authorization': 'Bearer %s' % self.key,
        })

        super().update(scraper=scraper)
