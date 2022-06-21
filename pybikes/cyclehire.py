# -*- coding: utf-8 -*-
# Copyright (c) 2022, Lluis Esquerda <eskerda@gmail.com>
# Copyright (C) 2016, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class CycleHire(BikeShareSystem):

    meta = {
        'system': 'Cycle Hire',
        'company': [
            'ITS',
        ]
    }

    def __init__(self, tag, meta, feed_url):
        super(CycleHire, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations = []

        DATA_RGX = r'Drupal\.settings\, (\{.*\})\)\;'

        page = scraper.request(self.feed_url)
        data = json.loads(re.search(DATA_RGX, page).group(1))
        markers = data.get('markers', [])
        for marker in markers:
            name = marker['title']
            latitude = float(marker['latitude'])
            longitude = float(marker['longitude'])
            nbikes = int(marker['avl_bikes'])
            ebikes = int(marker['avl_ebikes'])
            bikes = nbikes + ebikes
            free = int(marker['free_slots'])
            extra = {
                'uid': marker['nid'],
                'total_slots': int(marker['total_slots']),
                'has_ebikes': True,
                'ebikes': ebikes,
                'normal_bikes': nbikes,
                'online': marker['operative'] == '1',
            }

            station = BikeShareStation(name, latitude, longitude, bikes, free, extra)
            stations.append(station)

        self.stations = stations
