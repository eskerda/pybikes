# -*- coding: utf-8 -*-
# Original work Copyright (C) 2014, iomartin <iomartin@iomartin.net>
# Modified work Copyright (C) 2015 Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

from .base import BikeShareSystem, BikeShareStation
from . import utils

import re
import ast

__all__ = ['Samba', 'SambaNew']

USERAGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36"  # NOQA


class BaseSystem(BikeShareSystem):
    meta = {
        'system': 'Samba',
        'company': ['Mobilicidade Tecnologia LTD', 'Grupo Serttel LTDA']
    }

    def get_status(self, onlineStatus, operationStatus):
        # This is based on a function defined in the scrapped ASP page
        if operationStatus == 'EI' or operationStatus == 'EM':
            return 'maintenance/implementation'
        elif onlineStatus == 'A' and operationStatus == 'EO':
            return 'open'
        else:
            return 'closed'


class Samba(BaseSystem):
    sync = True
    _STATIONS_RGX = 'exibirEstacaMapa\((.*?)\);'

    def __init__(self, tag, meta, url):
        super(Samba, self).__init__(tag, meta)
        self.feed_url = url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(USERAGENT)

        html_data = scraper.request(self.feed_url,
                                    default_encoding='ISO-8859-1')
        # clean the data up
        html_data = re.sub(r'[\n|\r|\"]', '', html_data)

        station_data = re.findall(Samba._STATIONS_RGX, html_data)
        stations = []
        # The regex will also match for a function defined in the html. This
        # function is in the position of the array, and thus the [:-1]
        for data in station_data[:-1]:
            data = data.split(',')
            station = BikeShareStation()
            station.name = data[3]
            station.latitude = float(data[0])
            station.longitude = float(data[1])
            station.bikes = int(data[7])
            station.free = int(data[8]) - int(data[7])
            online_status = data[5]
            operation_status = data[6]
            station.extra = {
                'address': data[9],
                'uid': int(data[4]),
                'slots': int(data[8]),
                'status': self.get_status(online_status, operation_status)
            }
            stations.append(station)
        self.stations = stations


class SambaNew(BaseSystem):
    sync = True
    _STATIONS_RGX = "var\ beaches\ =\ \[(.*?)\,\];"

    def __init__(self, tag, meta, url):
        super(SambaNew, self).__init__(tag, meta)
        self.feed_url = url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(USERAGENT)

        html = scraper.request(self.feed_url)

        stations_html = re.findall(SambaNew._STATIONS_RGX, html)
        stations = ast.literal_eval(stations_html[0])
        '''
        Different from the original Samba class, th new one deals
        receives stations' information in the following format:
        [(0) name, (1) latitude, (2) longitude, (3) address,
        (4) address main line, (5) onlineStatus, (6) operationStatus,
        (7) available bikes (variable not being used in their code)
        (8) available bikes, (9) available bike stands,
        (10) internal station status, (11) path to image file, (12) stationId]
        '''
        self.stations = []
        for data in stations:
            station = BikeShareStation()
            station.name = data[0]
            station.latitude = float(data[1])
            station.longitude = float(data[2])
            station.bikes = int(data[8])
            station.free = int(data[9])
            online_status = data[5]
            operation_status = data[6]
            station.extra = {
                'address': data[4],
                'description': data[3],
                'status': self.get_status(online_status, operation_status)
            }
            self.stations.append(station)
