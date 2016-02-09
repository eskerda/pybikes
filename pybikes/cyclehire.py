# -*- coding: utf-8 -*-
# Copyright (C) 2016, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import lxml.html

from .base import BikeShareSystem, BikeShareStation
from . import utils

DATA_RGX = r'var sites = \[(.*?)\]\;'
STATIONS_RGX = r'\[(.*?)\]'


class CycleHire(BikeShareSystem):

    sync = True

    meta = {'system': 'Cycle Hire', 'company': 'Groundwork, ITS'}

    def __init__(self, tag, meta, feed_url):
        super(CycleHire, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        # var sites = [['<p><strong>001-Slough Train Station</strong></p>',
        #				 51.511350,-0.591562, ,
        #				 '<p><strong>001-Slough Train Station</strong></p>
        #					 <p>Number of bikes available: 11</p>
        #					 <p>Number of free docking points: 21</p>'], ...

        page = scraper.request(self.feed_url)
        data = re.findall(DATA_RGX, page)[0]
        raw_stations = re.findall(STATIONS_RGX, data)
        for raw_station in raw_stations:
            fields = raw_station.split(',')

            latitude = float(fields[1])
            longitude = float(fields[2])

            raw_status = fields[4]
            tree = lxml.html.fromstring(raw_status)
            name = tree.xpath('//p/strong/text()')[0]
            _, raw_bikes, raw_free = tree.xpath('//p/text()')
            bikes = int(re.search(r'\d+', raw_bikes).group())
            free = int(re.search(r'\d+', raw_free).group())

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       {})
            stations.append(station)
        self.stations = stations