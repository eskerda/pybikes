# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
import re

from lxml import html
from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['BiciPalma']

COOKIE_URL = "http://83.36.51.60:8080/eTraffic3/Control?act=mp"
DATA_URL = "http://83.36.51.60:8080/eTraffic3/DataServer?ele=equ&type=401&li=2.6288892088318&ld=2.6721907911682&ln=39.58800054245&ls=39.55559945755&zoom=15&adm=N&mapId=1&lang=es"
NAME_UID_RE = "\[(\d+)\] (.*)"

headers = {
'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2',
'Referer':'http://83.36.51.60:8080/eTraffic3/Control?act=mp'
}

class BiciPalma(BikeShareSystem):
    meta = {}

    def __init__(self, tag, meta):
        super(BiciPalma, self).__init__(tag, meta)

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.headers.update(headers)

        # First visit the cookie setter
        scraper.request(COOKIE_URL)
        # We should have now a nice cookie in our header

        # Wow many fuzzle, so ugly
        fuzzle = scraper.request(DATA_URL)
        markers = json.loads(fuzzle)

        stations = []
        for marker in markers:
            # id = marker['id']
            # Seems that this id is just incremental, and not related to the
            # system at all.. discrating until further notiche?

            # [uid] name as [77] THIS IS HORRID SHIT
            uid, name = re.findall(NAME_UID_RE, marker['title'])[0]

            stat_fuzzle = html.fromstring(marker['paramsHtml'])
            stats = stat_fuzzle.cssselect('div#popParam')
            ints = []
            for i in range(1,6):
                ints.append(int([a for a in stats[i].itertext()][1].strip()))

            station = BikeShareStation()
            station.latitude = float(marker['realLat'])
            station.longitude = float(marker['realLon'])
            station.name = utils.sp_capwords(re.sub('\ *-\ *',' - ',name).title())
            station.bikes = ints[1]
            station.free = ints[4]
            station.extra = {
                'uid': int(uid),
                'enabled': marker['enabled'],
                'used_slots': ints[2],
                'faulty_slots': ints[3]
            }
            stations.append(station)

        self.stations = stations

