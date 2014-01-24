# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import re

from lxml import html

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Emovity']

RE_INFO = "var html\d+ =\'(.*)\'"
RE_LATLNG = 'var pBikes\d+= new GLatLng\((.*)\,(.*)\)'

class Emovity(BikeShareSystem):
    sync = True
    meta = {
        'system': 'Emovity',
        'company': 'ICNITA S.L.'
    }

    def __init__(self, tag, feed_url, meta):
        super(Emovity, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        fuzzle = scraper.request(self.feed_url)
        latlngs = re.findall(RE_LATLNG, fuzzle)
        infos = re.findall(RE_INFO, fuzzle)
        stations = []

        for i in range(0, len(latlngs)):
            tree = html.fromstring(infos[i])

            station = BikeShareStation(i)
            station.latitude = float(latlngs[i][0])
            station.longitude = float(latlngs[i][1])
            station.name = tree[1].text
            station.bikes = int(re.findall(".*: (\d+)", tree[2].text)[0])
            station.free  = int(re.findall(".*: (\d+)", tree[3].text)[0])
            station.extra = {
                'uid': re.findall("(\d+)\-.*", tree[0].text)[0]
            }
            stations.append(station)
        self.stations = stations
