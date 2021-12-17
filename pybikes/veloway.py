# -*- coding: utf-8 -*-
# Copyright (C) 2010-2021, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

try:
    # Python 2
    from urllib import unquote_plus
except ImportError:
    # Python 3
    from urllib.parse import unquote_plus

from lxml import html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.exceptions import InvalidStation


class BaseSystem(BikeShareSystem):
    meta = {
        'system': 'Veloway',
        'company': ['Veolia']
    }


class Veloway(BaseSystem):
    def __init__(self, tag, meta, feed_url):
        super(Veloway, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        data = json.loads(scraper.request(self.feed_url))
        stations = []
        for info in data['stand']:
            try:
                station = VelowayStation(info)
            except InvalidStation:
                continue
            stations.append(station)
        self.stations = stations


class VelowayStation(BikeShareStation):
    """ A "stand" is like:
        {
          "wcom": "Boulevard+Rene+Cassin+(face+au+n%c2%b0100)+",
          "disp": "1",      # available
          "neutral": "0",   # neutralized or under construction, unused here
          "lng": "7.2170729637146",
          "lat": "43.6695556640625",
          "tc": "15",       # total capacity
          "ac": "15",       # available capacity
          "ap": "7",        # available parking
          "ab": "8",        # available bike
          "id": "11",
          "name": "Station+n%c2%b0011"
        }
    """
    def __init__(self, info):
        super(VelowayStation, self).__init__()
        # careful unicode to str conversion before unquoting
        self.name = unquote_plus(str(info['name']))
        self.bikes = int(info['ab'])
        self.free = int(info['ap'])
        self.latitude = float(info['lat'])
        self.longitude = float(info['lng'])
        self.extra = {
            'uid': int(info['id']),
            'slots': int(info['tc']),
            'slots_available': int(info['ac']),
            'online': int(info['disp']) == 1,
        }

        # careful unicode to str conversion before unquoting
        if info['wcom']:
            self.extra['address'] = unquote_plus(str(info['wcom']))

        if self.latitude is None or self.longitude is None:
            raise InvalidStation('A station needs a lat/lng to be defined!')
        if self.latitude == 0 and self.longitude == 0:
            raise InvalidStation('A station can\'t be located in Atlantic Ocean!')
