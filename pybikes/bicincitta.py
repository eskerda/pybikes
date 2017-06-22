# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import re
import HTMLParser

from .base import BikeShareSystem, BikeShareStation
from . import utils


class Bicincitta(BikeShareSystem):
    sync = True
    _RE_INFO="RefreshMap\((.*?)\)\;"
    _endpoint = "http://bicincitta.tobike.it/frmLeStazioni.aspx?ID={id}"

    meta = {
        'system': 'Bicincittà',
        'company': ['Comunicare S.r.l.']
    }

    def __init__(self, tag, meta, url):
        super(Bicincitta, self).__init__(tag, meta)
        self.url = url
        if not isinstance(self.url, list):
            self.url = [self.url]

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        self.stations = []
        for url in self.url:
            stations = Bicincitta._getComuneStations(url, scraper)
            self.stations += stations

    @staticmethod
    def _getComuneStations(url, scraper):
        data = scraper.request(url)
        raw = re.findall(Bicincitta._RE_INFO, data)
        info = raw[0].split('\',\'')
        info = map(lambda chunk: chunk.split('|'), info)
        # Yes, this is a joke
        names = info[5]
        descs = info[7]
        lats = info[3]
        lngs = info[4]
        bikes = info[6]
        status = info[8]
        return [BicincittaStation(name, desc, float(lat), float(lng),
                bikes.count('4'), bikes.count('0'), stat)
                for name, desc, lat, lng, bikes, stat in
                zip(names, descs, lats, lngs, bikes, status)]


class BicincittaStation(BikeShareStation):

    station_statuses = {
        0: 'online',
        1: 'maintenance',
        2: 'offline',
        3: 'under construction',
        4: 'planned',
    }


    def __init__(self, name, description, lat, lng, bikes, free, status):
        super(BicincittaStation, self).__init__()
        if name[-1] == ":":
            name = name[:-1]

        # There's a bug that sometimes will give lat / lngs on 1E6
        # http://www.tobike.it/frmLeStazioni.aspx?ID=22
        # search for (7676168)
        lat = float(lat)
        lng = float(lng)
        if lat > 85.0 or lat < -85.0:
            lat = lat / 1E6
        if lng > 180.0 or lng < -180.0:
            lng = lng / 1E6

        self.name        = utils.clean_string(name)
        self.latitude    = lat
        self.longitude   = lng
        self.bikes       = int(bikes)
        self.free        = int(free)

        self.extra       = {
            'status': BicincittaStation.station_statuses[int(status)]
        }

        if description:
            self.extra['description'] = utils \
                    .clean_string(description) \
                    .rstrip(' :')
