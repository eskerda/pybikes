# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re

from .base import BikeShareSystem, BikeShareStation
from . import utils
from contrib import TSTCache

__all__ = ['Baksi', 'BaksiStation']

# Atomic bomb rgx
# Tomorrow
# Use unicode to transform to utf-8
ID_NAME_RGX="[0-9]*\-[a-zA-Z0-9\s]*"
STATUS_RGX=""
DOCKS_BIKES_RGX=""
LAT_LNG_RGX=""

USERAGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36"

cache = TSTCache(delta=60)

class Baksi(BikeShareSystem):
    #sync = ???
    #unifeed = ???
    #authend or authe...(dont remember) not needed
    meta = {
        'system': 'Baksi',
        'company': ['Baksi Bike Sharing System']
    }

    # init is ready
    def __init__(self, tag, meta, city_uid, feed_url):
        super(Baksi, self).__init__(tag, meta)
        self.feed_url=feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(USERAGENT)

        html_data=scraper.request(self.feed_url)

        id_name=re.findall(ID_NAME_RGX, html_data)
        status=re.findall(STATUS_RGX, html_data)
        docks_bikes=re.findall(DOCKS_BIKES_RGX, html_data)
        geopoints=re.findall(LAT_LNG_RGX, html_data)



class BaksiStation(BikeShareStation):
    def __init__(self, info):
        super(BaksiStation, self).__init__()

