# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import re

from lxml import html

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Emovity']


class Emovity(BikeShareSystem):
    sync = True
    meta = {
        'system': 'Emovity',
        'company': ['ICNITA S.L.']
    }

    def __init__(self, tag, feed_url, meta):
        super(Emovity, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        fuzzle = scraper.request(self.feed_url)
        data = zip(
            re.findall(r"addMarker\(\d+,(\d+.\d+),(\d+.\d+)", fuzzle),
            re.findall(r"html\[\d+\]='(.*?)';", fuzzle)
        )
        stations = []
        for latlng, html_fuzzle in data:
            dom = html.fromstring(html_fuzzle)
            text = dom.xpath('//div/text()')
            station = BikeShareStation()
            station.latitude = float(latlng[0])
            station.longitude = float(latlng[1])
            station.name = text[1]
            station.bikes = int(re.search(r'\d+', text[2]).group())
            station.free = int(re.search(r'\d+', text[3]).group())
            station.extra = {
                'uid': re.search(r'^\d+', text[0]).group()
            }
            stations.append(station)
        self.stations = stations
