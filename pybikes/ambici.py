# -*- coding: utf-8 -*-
# Copyright (C) 2010-2023, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs


FEED_URL = "https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bs/gbfs.json"

class Ambici(Gbfs):
    meta = {
        'system': 'Ambici',
        'name': 'Ambici',
        'company': [
            'Nextbike GmbH',
            'TIER Mobility SE',
            'Transports Metropolitans de Barcelona',
            'Projectes i Serveis de Mobilitat S.A',
        ]
    }

    unifeed = True

    def __init__(self, * args, ** kwargs):
        super().__init__(* args, feed_url=FEED_URL, ** kwargs)
