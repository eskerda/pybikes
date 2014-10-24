# -*- coding: utf-8 -*-
# Copyright (C) 2014, iomartin <iomartin@iomartin.net>
# Distributed under the LGPL license, see LICENSE.txt

from .base import BikeShareSystem, BikeShareStation
from . import utils

import re

__all__ = ['CicloSampa', 'CicloSampaStation']

STATIONS_RGX = 'setEstacao\((.*?)\);'
USERAGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36"

class CicloSampa(BikeShareSystem):
    sync = True
    meta = {
        'system': 'CicloSampa',
        'company': ['Bradesco Seguros']
    }

    def __init__(self, tag, meta, url):
        super(CicloSampa, self).__init__(tag, meta)
        self.feed_url = url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(USERAGENT)

        html_data = scraper.request(self.feed_url)
        # clean the data up
        html_data = ''.join(html_data).replace('"', '')

        stations = re.findall(STATIONS_RGX, html_data)

        self.stations = []

        for station in stations:
            self.stations.append(CicloSampaStation(station.split(',')))

class CicloSampaStation(BikeShareStation):
    def __init__(self, data):
        '''
        data is a list of strings, in the following order:
            [latitude, longitude, stationId, name, address, availableBikes,
             bike capacity]
        '''
        super(CicloSampaStation, self).__init__(0)
        self.name = data[3]
        self.latitude = float(data[0])
        self.longitude = float(data[1])
        self.bikes = int(data[5])
        self.free = int(data[6])
        self.extra = {
            'address': data[4],
            'uid': int(data[2]),
            'slots': int(data[6]) + int(data[5])
        }
