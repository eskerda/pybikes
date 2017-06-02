# -*- coding: utf-8 -*-
# Copyright (C) 2017, aronsky <aronsky@gmail.com>

import re
from lxml import etree

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes import utils


class FSMSystem(BikeShareSystem):
    sync = True
    unifeed = False

    meta = {
        'system': 'fsm',
        'company': ['FSM Ground Services Ltd.']
    }

    def __init__(self, tag, meta, feed_url):
        super(FSMSystem, self).__init__(tag, meta)

        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        stations = []

        data = scraper.request(self.feed_url)
        dom = etree.fromstring(data.encode('utf-8'))
        stations = self.get_stations(dom)
        self.stations = list(stations)

    def get_stations(self, dom):
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        for placemark in dom.xpath('//kml:Placemark', namespaces=ns):
            name = placemark.findtext('kml:name', namespaces=ns)
            info = placemark.findtext('kml:description', namespaces=ns)
            station_uid, bikes, free = map(int,
                re.findall(r'\w+\:\s*(\d+)', info)
            )
            longitude, latitude = placemark.findtext(
                'kml:Point/kml:coordinates',
                namespaces=ns
            ).split(',')
            latitude = float(latitude)
            longitude = float(longitude)
            extra = {
                'uid': station_uid,
            }

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            yield station
