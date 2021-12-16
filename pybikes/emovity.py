# -*- coding: utf-8 -*-
# Copyright (C) 2010-2021, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import re

from lxml import html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

# this time and age and we are still banning requests based on user agent lol
UA = 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4572.0 Safari/537.36'
# nobody dares touch this site  with a ten-foot pole
STATION_RE = r'addMarker\((\d+\.\d+),(\d+.\d+),(\d+),(\d+),\'(.*)\'\)\;'

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
        scraper = scraper or PyBikesScraper()
        scraper.setUserAgent(UA)

        fuzzle = scraper.request(self.feed_url)
        data = re.findall(STATION_RE, fuzzle)

        self.stations = list(map(lambda d: EmovityStation(* d), data))


class EmovityStation(BikeShareStation):
    def __init__(self, latitude, longitude, bikes, free, fuzzle):
        dom = html.fromstring(fuzzle)
        text = dom.xpath('//div/text()')
        name = text[0]
        uid = next(iter(re.findall(r'(\d+)\s*-', name)))

        super(EmovityStation, self).__init__(
            name=text[0],
            latitude=float(latitude),
            longitude=float(longitude),
            bikes=int(bikes),
            free=int(free),
            extra={'uid': uid},
        )
