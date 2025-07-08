# -*- coding: utf-8 -*-
# Copyright (C) 2025, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs


FEED_URL = "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_{domain}/gbfs.json"

class NextbikeGbfs(Gbfs):
    meta = {
        'system': 'Nextbike',
        # Default name unless specified in json
        'name': 'Nextbike',
        'company': [
            'Nextbike GmbH',
        ]
    }

    def __init__(self, domain, * args, ** kwargs):
        feed_url = FEED_URL.format(domain=domain)
        super().__init__(* args, feed_url=feed_url, ** kwargs)
