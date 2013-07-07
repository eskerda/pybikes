# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
from pyquery import PyQuery as pq

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['SmartBike','Bizi','BiziStation']

LAT_LNG_RGX = 'point \= new GLatLng\((.*?)\,(.*?)\)'
ID_ADD_RGX = 'idStation\=(.*)\&addressnew\=(.*)\&s\_id\_idioma'
ID_ADD_RGX_V = 'idStation\=\"\+(.*)\+\"\&addressnew\=(.*)\+\"\&s\_id\_idioma'

class BaseSystem(BikeShareSystem):
    meta = {
        'system': 'SmartBike',
        'company': 'ClearChannel'
    }

class SmartBike(BaseSystem):
    pass
    
class Bizi(BaseSystem):
    sync = False
    list_url = "/localizaciones/localizaciones.php"
    station_url = "/CallWebService/StationBussinesStatus.php"

    def __init__(self, tag, meta, root_url, 
                 list_url = None, station_url = None, v = 2):
        super(Bizi, self).__init__(tag, meta)
        self.root_url = root_url
        if list_url is not None:
            self.list_url = list_url

        if station_url is not None:
            self.station_url = station_url

        self.v = v

    def update(self, scraper = None):

        if scraper is None:
            scraper = utils.PyBikesScraper()

        raw = scraper.request(
            "{0}{1}".format(self.root_url, self.list_url)
        )
        geopoints = re.findall(LAT_LNG_RGX, raw)
        if (self.v == 1):
            ids_addrs = re.findall(ID_ADD_RGX_V, raw)
        else:
            ids_addrs = re.findall(ID_ADD_RGX, raw)
        stations = []

        for index, geopoint in enumerate(geopoints):
            station = BiziStation(index)
            station.latitude = float(geopoint[0])
            station.longitude = float(geopoint[1])
            uid = int(ids_addrs[index][0])
            station.extra = {
                'uid': uid,
                'token': ids_addrs[index][1]
            }
            station.parent = self
            stations.append(station)
        
        self.stations = stations

class BiziStation(BikeShareStation):
    def update(self, scraper = None):

        if scraper is None:
            scraper = utils.PyBikesScraper()


        super(BiziStation, self).update()
        raw = scraper.request( method="POST",
                url = "{0}{1}".format(self.parent.root_url, self.parent.station_url),
                data = {
                    'idStation': self.extra['uid'],
                    'addressnew': self.extra['token']    
                }
        )
        dom = pq(raw)
        availability = dom('div').eq(2).text().split(':')
        name = dom('div').eq(1).text().replace('<br>','').strip()
        self.name = name.encode('utf-8')
        self.bikes = int(availability[1].lstrip())
        self.free = int(availability[2].lstrip())
        
        return True
