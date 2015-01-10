# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
import urllib

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Veloway','VelowayStation']

class BaseSystem(BikeShareSystem):
    meta = {
        'system': 'Veloway',
        'company': 'Veolia'
    }

class Veloway(BaseSystem):
    def __init__(self, tag, meta, feed_url):
        super(Veloway, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
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
        self.name = urllib.unquote_plus(info['name'].replace('%c2', ''))
        self.bikes = int(info['ab'])
        self.free = int(info['ap'])
        self.latitude = float(info['lat'])
        self.longitude = float(info['lng'])
        self.extra = {
            'uid': int(info['id']),
            'address': fix_name(info['wcom']),
            'slots': int(info['tc']),
            'slots_available': int(info['ac']),
        }

        if int(info['disp']) == 1:
            self.extra['status'] = 'OPEN'
        else:
            self.extra['status'] = 'CLOSED'

        if self.latitude is None or self.longitude is None:
            raise Exception('A station needs a lat/lng to be defined!')
        if self.latitude == 0 and self.longitude == 0:
            raise Exception('A station can\'t be located in Atlantic Ocean!')

def fix_name(title):
    """ WTF... From http://www.velobleu.org/cartoV2/js/libVeloway.js
        while (html.indexOf("+") != -1) {
                html = html.replace("+", " ");
                }
        while (html.indexOf("n%c2%b0") != -1) {
                html = html.replace("n%c2%b0", "n°");
                }
        while (html.indexOf("%c3%a9") != -1) {
                html = html.replace("%c3%a9", "é");
                }
        while (html.indexOf("%c3%b4") != -1) {
                html = html.replace("%c3%b4", "ô");
                }
        while (html.indexOf("%c3%a7") != -1) {
                html = html.replace("%c3%a7", "ç");
                }
        while (html.indexOf("%3a") != -1) {
                html = html.replace("%3a", ":");
                }
        return html;
    """
    dic = {
        '+': u' ',
        '%c2%b0': u'°',
        '%c3%a0': u'à',
        '%c3%a7': u'ç',
        '%c3%a8': u'è',
        '%c3%a9': u'é',
        '%c3%b4': u'ô',
        '%e2%80%99': u'\'',
        '%27': u'\'',
        '%2f': u'/',
        '%3a': u':'
    }

    for i, j in dic.iteritems():
        title = title.replace(i, j)

    return title
