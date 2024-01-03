# -*- coding: utf-8 -*-
# Copyright (C) 2010-2023, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from lxml import etree

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


class DecoBike(Bounded, BikeShareSystem):
    sync = True

    meta = {
        'system': 'DecoBike',
        'company': ['DecoBike LLC']
    }

    headers = {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        'X-Requested-With': 'com.citibike.miami',
    }

    def __init__(self, tag, meta, feed_url, bbox=None):
        super(DecoBike, self).__init__(tag, meta, bounds=bbox)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        raw = scraper.request(self.feed_url, headers=self.headers)
        tree = etree.fromstring(raw)
        stations = []
        for location in tree.xpath('//location'):
            station = BikeShareStation()
            uid     = location.find('Id').text
            address = location.find('Address').text

            station.name      = "%s - %s" % (uid, address)
            station.latitude  = float(location.find('Latitude').text)
            station.longitude = float(location.find('Longitude').text)
            station.bikes     = int(location.find('Bikes').text)
            station.free      = int(location.find('Dockings').text)

            station.extra = {
                'uid': uid,
                'address': address
            }

            stations.append(station)

        self.stations = stations
