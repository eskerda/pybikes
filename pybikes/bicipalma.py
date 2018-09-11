# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from pybikes import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2',   # NOQA
}

API_INFO_URL = 'http://www.mobipalma.mobi/mobilitat/bicipalma/'
# Even though we can get this from API info, we do not want outside control
# over which domains we access
API_BASE_URL = 'https://api.mobipalma.mobi/1.0'
API_STATIONS_URL = '{baseurl}/bicipalma'.format(baseurl=API_BASE_URL)
API_STATUS_URL = '{baseurl}/bicipalma/estados'.format(baseurl=API_BASE_URL)


class BiciPalma(BikeShareSystem):
    meta = {}

    def __init__(self, tag, meta):
        super(BiciPalma, self).__init__(tag, meta)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        scraper.headers.update(headers)

        api_info_data = scraper.request(API_INFO_URL)
        api_info_match = re.search(r'MobipalmaMapa\((.*})\);', api_info_data)
        if not api_info_match:
            raise Exception('Mobipalma API info not found on website')

        api_info = json.loads(api_info_match.group(1))
        scraper.headers.update({
            'Authorization': 'Bearer %s' % api_info['token_data']['token'],
        })
        stations = json.loads(scraper.request(API_STATIONS_URL))
        status = json.loads(scraper.request(API_STATUS_URL))

        stations = {s['id']: s for s in stations}
        status = {s['id']: s for s in status}

        stations = [
            (stations[uid], status[uid]) for uid in stations.keys()
        ]

        self.stations = list(self.parse_stations(stations))

    def parse_stations(self, stations):
        for info, status in stations:
            info.update(status)
            station = BiciPalmaStation(info)
            yield station


class BiciPalmaStation(BikeShareStation):
    def __init__(self, info):
        super(BiciPalmaStation, self).__init__()

        self.name = info['nombre_estacion']
        self.latitude = float(info['latitud'])
        self.longitude = float(info['longitud'])
        self.bikes = int(info['bicis_libres'])
        self.free = int(info['anclajes_libres'])
        self.extra = {
            'uid': info['id'],
            'online': info['comunica'] and not info['cerrado'],
        }
