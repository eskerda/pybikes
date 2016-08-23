# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from .base import BikeShareSystem, BikeShareStation
from . import utils
from contrib import TSTCache

__all__ = ['Baksi', 'BaksiStation']

cache = TSTCache(delta=60)

class Baksi(BikeShareSystem):
    #sync =
    #unifeed =
    meta = {
        'system': 'Baksi',
        'company': ['Baksi Bike Sharing System']
    }

    def __init__(self, tag, meta, city_uid, feed_url):
        super(Baksi, self).__init__(tag, meta)
        self.feed_url=feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()


class BaksiStation(BikeShareStation):
    def __init__(self, info):
        pass
