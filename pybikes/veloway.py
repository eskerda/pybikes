# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json
import urllib
from lxml import html

from .base import BikeShareSystem, BikeShareStation
from . import utils


class BaseSystem(BikeShareSystem):
    meta = {
        'system': 'Veloway',
        'company': 'Veolia'
    }


class Veloway(BaseSystem):
    def __init__(self, tag, meta, feed_url):
        super(Veloway, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        data = json.loads(scraper.request(self.feed_url))
        stations = []
        for info in data['stand']:
            try:
                station = VelowayStation(info)
            except Exception:
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
        self.name = urllib.unquote_plus(
            info['name'].decode('latin-1').encode('utf-8')
        )
        self.bikes = int(info['ab'])
        self.free = int(info['ap'])
        self.latitude = float(info['lat'])
        self.longitude = float(info['lng'])
        self.extra = {
            'uid': int(info['id']),
            'slots': int(info['tc']),
            'slots_available': int(info['ac']),
        }

        if int(info['disp']) == 1:
            self.extra['status'] = 'OPEN'
        else:
            self.extra['status'] = 'CLOSED'

        if info['wcom']:
            self.extra['address'] = urllib.unquote_plus(
                info['wcom'].decode('latin-1').encode('utf-8')
            )

        if self.latitude is None or self.longitude is None:
            raise Exception('A station needs a lat/lng to be defined!')
        if self.latitude == 0 and self.longitude == 0:
            raise Exception('A station can\'t be located in Atlantic Ocean!')


class VelowayDrupal(Veloway):

    # Station 01 - Gare SNCF (Vélos libres : 9 Places libres
    station_rgx = (ur'Station\s+(?P<id>\d+)\s*-\s*'
                   ur'(?P<name>.+)\s+'
                   ur'\(Vélos\s+libres\s*:\s*(?P<bikes>\d+)\s+'
                   ur'Places\s+libres\s*:\s*(?P<free>\d+)\)')

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        _html = scraper.request(self.feed_url)
        dom = html.fromstring(_html)
        # Data is duplicated...
        markers = dom.xpath("""
            (//ul[li[@data-gmapping]])[1]//
                li[@data-gmapping]
        """)
        stations = []
        for marker in markers:
            g_map = json.loads(marker.get('data-gmapping'))
            lat = float(g_map['latlng']['lat'])
            lng = float(g_map['latlng']['lng'])

            fuzzle = ''.join(marker.xpath('.//text()')).strip()
            data = re.search(self.station_rgx, fuzzle)

            uid = data.group('id')
            name = data.group('name')
            bikes = int(data.group('bikes'))
            free = int(data.group('free'))

            extra = {
                'uid': uid
            }
            station = BikeShareStation(name, lat, lng, bikes, free, extra)
            stations.append(station)
        self.stations = stations
