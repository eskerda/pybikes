# -*- coding: utf-8 -*-
# Copyright (C) 2017, aronsky <aronsky@gmail.com>

from xml.dom import minidom

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes import utils


class TeloFun(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'telofun',
        'company': ['FSM Ground Services Ltd.']
    }

    def __init__(self, tag, meta, feed_url):
        super(TeloFun, self).__init__(tag, meta)

        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        stations = []

        data = scraper.request(self.feed_url)
        dom = minidom.parseString(data.encode('utf-8', errors='ignore'))
        stations = self.get_stations(dom)
        self.stations = list(stations)

    def get_stations(self, dom):
        for placemark in dom.getElementsByTagName('Placemark'):
            name = placemark.getElementsByTagName('name')[0].childNodes[0] \
                   .nodeValue
            info = placemark.getElementsByTagName('description')[0] \
                   .childNodes[0].nodeValue
            station_code, bikes, free = [
                    int(line.strip().split(':')[-1].strip()) \
                    for line in info.strip().split('<br/>') if len(line) > 0
                    ]
            latitude, longitude = placemark.getElementsByTagName('Point')[0] \
                                  .childNodes[0].childNodes[0].nodeValue \
                                  .split(',')
            latitude = float(latitude)
            longitude = float(longitude)
            extra = {
                'code': station_code,
                'slots': bikes + free
            }

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            yield station
