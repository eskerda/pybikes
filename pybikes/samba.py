# -*- coding: utf-8 -*-
# Original work Copyright (C) 2014, iomartin <iomartin@iomartin.net>
# Modified work Copyright (C) 2015 Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Modified work Copyright (C) 2023 Martín González Gómez <m@martingonzalez.net>
# Distributed under the LGPL license, see LICENSE.txt

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded

import re
import ast

USERAGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36"  # NOQA


class Samba(Bounded, BikeShareSystem):
    meta = {
        'system': 'Samba',
        'company': ['Mobilicidade Tecnologia LTD', 'Grupo Serttel LTDA']
    }

    def __init__(self, tag, meta, url, bbox=None):
        super(Samba, self).__init__(tag, meta, bounds=bbox)
        self.feed_url = url

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()
        scraper.setUserAgent(USERAGENT)

        html = scraper.request(self.feed_url)

        stations_html = re.findall("var\ beaches\ =\ \[(.*?)\,\];", html)
        stations_data = ast.literal_eval(stations_html[0])

        stations = []

        for station in stations_data:
            stations.append(SambaStation(station))

        self.stations = stations


class SambaStation(BikeShareStation):
    def get_status(self, onlineStatus, operationStatus):
        # This is based on a function defined in the scrapped ASP page
        if operationStatus == 'EI' or operationStatus == 'EM':
            return 'maintenance/implementation'
        elif onlineStatus == 'A' and operationStatus == 'EO':
            return 'open'
        else:
            return 'closed'

    def __init__(self, data):
        super(SambaStation, self).__init__()

        self.name = data[0]
        self.latitude = float(data[1])
        self.longitude = float(data[2])
        self.bikes = int(data[8])
        self.free = int(data[9])
        online_status = data[5]
        operation_status = data[6]
        self.extra = {
            'address': data[4],
            'description': data[3],
            'status': self.get_status(online_status, operation_status)
        }
