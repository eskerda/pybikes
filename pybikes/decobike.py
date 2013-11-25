# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
import codecs

from pyquery import PyQuery as pq

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['DecoBike']

FEED = "{endpoint}/playmoves.xml"

class DecoBike(BikeShareSystem):
    sync = True

    meta = {
        'system': 'DecoBike',
        'company': 'DecoBike LLC'
    }

    def __init__(self, tag, meta, endpoint):
        super(DecoBike, self).__init__(tag, meta)
        self.feed_url = FEED.format(endpoint = endpoint)

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        raw = scraper.request(self.feed_url)
        dom = pq(raw, parser = 'xml')
        stations = []
        for location in dom('location'):
            station = BikeShareStation(0)
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

