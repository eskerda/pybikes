# -*- coding: utf-8 -*-
# Copyright (C) 2014, iomartin <iomartin@iomartin.net>
# Distributed under the LGPL license, see LICENSE.txt

from .base import BikeShareSystem, BikeShareStation
from . import utils

import re

__all__ = ['Samba', 'SambaStation']

STATIONS_RGX = 'exibirEstacaMapa\((.*?)\)'
USERAGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36"

class Samba(BikeShareSystem):
    sync = True
    meta = {
        'system': 'Samba',
        'company': ['Mobilicidade Tecnologia LTD', 'Grupo Serttel LTDA']
    }

    def __init__(self, tag, meta, url):
        super(Samba, self).__init__(tag, meta)
        self.feed_url = url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(USERAGENT)

        html_data = scraper.request(self.feed_url)
        # clean the data up
        html_data = ''.join(html_data).replace('\n', '').replace('\r', '').replace('"', '')

        stations = re.findall(STATIONS_RGX, html_data)

        self.stations = []

        # The regex will also match for a function defined in the html. This
        # function is in the position of the array, and thus the [:-1]
        for station in stations[:-1]:
            self.stations.append(SambaStation(station.split(',')))

class SambaStation(BikeShareStation):
    def __init__(self, data):
        '''
        data is a list of strings, in the following order:
            [latitude, longitude, icon (path to image file, which we ignore),
             name, stationId, onlineStatus, operationStatus, availabeBikes,
             bike capacity, address]
        '''
        super(SambaStation, self).__init__(0)
        self.name = data[3]
        self.latitude = float(data[0])
        self.longitude = float(data[1])
        self.bikes = int(data[7])
        self.free = int(data[8]) - self.bikes
        self.extra = {
            'address': data[9],
            'status': self.get_status(data[5], data[6]),
            'uid': data[4]
        }

    def get_status(self, onlineStatus, operationStatus):
        # This is based on a function defined in the scrapped ASP page
        if operationStatus == 'EI' or operationStatus == 'EM':
            return 'maintenance/implementation'
        elif onlineStatus == 'A' and operationStatus == 'EO':
            return 'open'
        else:
            return 'closed'
