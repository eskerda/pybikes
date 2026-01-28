# -*- coding: utf-8 -*-
# Copyright (C) 2010-2026, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs


BASE_URL = "https://api.cyclocity.fr/contracts/{contract}/gbfs/gbfs.json"


class Cyclocity(Gbfs):

    meta = {
        'system': 'Cyclocity',
        'company': ['JCDecaux'],
        'license': {
            'name': 'Open Licence',
            'url': 'https://developer.jcdecaux.com/#/opendata/licence'
        },
        'source': 'https://developer.jcdecaux.com'
    }

    def __init__(self, * args, contract, ** kwargs):
        feed_url = BASE_URL.format(contract=contract.lower())
        super().__init__(*args, feed_url=feed_url, ** kwargs)
