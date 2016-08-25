# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re

from .base import BikeShareSystem, BikeShareStation
from . import utils
from contrib import TSTCache

__all__ = ['Baksi', 'BaksiStation']

ID_NAME_RGX="([0-9]+)\-([\w\s.()-]+)\'"
STATUS_RGX="Durum\ [&nbsp;]+\ (\w+)"
DOCKS_RGX="Park[&nbsp;]+([0-9]+)"
BIKES_RGX="Bisiklet[&nbsp;]+([0-9]+)"
LAT_LNG_RGX="([\s0-9.]+)\',\ \'([\s0-9.]+)"

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

    def __init__(self, tag, meta, city_uid, feed_url):
        super(Baksi, self).__init__(tag, meta)
        self.feed_url=feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(USERAGENT)

        html_data=scraper.request(self.feed_url, raw=True)

        """Fetch data
        """
        id_name=re.findall(ID_NAME_RGX, html_data, re.UNICODE)
        status=re.findall(STATUS_RGX, html_data, re.UNICODE)
        docks=re.findall(DOCKS_RGX, html_data, re.UNICODE)
        bikes=re.findall(BIKES_RGX, html_data, re.UNICODE)
        geopoints=re.findall(LAT_LNG_RGX, html_data, re.UNICODE)

        """Refine output
        """
        station_id, name=zip(*id_name)
        status=["Active" if out=="Aktif" else "Inactive" for out in status]
        docks=[int(i) for i in docks]
        bikes=[int(i) for i in bikes]
        latitude, longitude=zip(*geopoints)

        for data in zip(station_id, name, status, docks, bikes, latitude, longitude):
            self.stations.append(BaksiStation(data))


class BaksiStation(BikeShareStation):
    def __init__(self, data):
        super(BaksiStation, self).__init__()
        self.station_id=data[0]
        self.name=data[1]
        self.status=data[2]
        self.bikes=data[3]+data[4]
        self.free=data[4]
        self.latitude=data[5]
        self.longitude=data[6]
