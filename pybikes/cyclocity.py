# -*- coding: utf-8 -*-
# Copyright (C) 2025, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs


FEED_URL = "https://api.cyclocity.fr/contracts/{contract}/gbfs/gbfs.json"

class Cyclocity(Gbfs):
    meta = {
        # Default name unless specified in json
        'system': 'Cyclocity',
        'name': 'Cyclocity',
        'company': [
            'JCDecaux',
        ]
    }

    def __init__(self, contract, * args, ** kwargs):
        feed_url = FEED_URL.format(contract=contract)
        super().__init__(* args, feed_url=feed_url, ** kwargs)
