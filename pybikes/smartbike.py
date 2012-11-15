# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
from pyquery import PyQuery as pq
import urllib.parse

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['SmartBikeSystem', 'SmartBiziSystem']

LAT_LNG_RGX = b'point \= new GLatLng\((.*?)\,(.*?)\)'
ID_ADD_RGX = b'idStation\=(.*)\&addressnew\=(.*)\&s\_id\_idioma'


class SmartBikeSystem(BikeShareSystem):
    meta = {
        'system': 'SmartBike',
        'company': 'ClearChannel'
    }

class SmartBiziSystem(SmartBikeSystem):
    sync = False
    list_url = "/localizaciones/localizaciones.php"
    station_url = "/CallWebService/StationBussinesStatus.php"

    def __init__(self, tag, meta, root_url, list_url = None, station_url = None):
        super(SmartBiziSystem, self).__init__(tag, meta)
        self.root_url = root_url
        if list_url is not None:
            self.list_url = list_url

        if station_url is not None:
            self.station_url = station_url

    def update(self):
        raw = self._scrapper.request(
            "{0}{1}".format(self.root_url, self.list_url)
        ).read()
        geopoints = re.findall(LAT_LNG_RGX, raw)
        ids_addrs = re.findall(ID_ADD_RGX, raw)
        stations = []
        for index, geopoint in enumerate(geopoints):
            station = SmartBiziStation(index)
            station.latitude = float(geopoint[0])
            station.longitude = float(geopoint[1])
            try: 
                uid = int(ids_addrs[index][0])
            except ValueError:
                #Shit ecobici..
                uid = int(re.sub(r'[\"|\+]','',ids_addrs[index][0].decode('utf-8')))

            station.extra = {
                'uid': uid,
                'token': ids_addrs[index][1]
            }
            stations.append(station)
        
        self.stations = stations

class SmartBiziStation(BikeShareStation):
    def update(self, parent):
        super(SmartBiziStation, self).update()
        raw = parent._scrapper.request(
            "{0}{1}".format(parent.root_url, parent.station_url),
            urllib.parse.urlencode({
                'idStation': self.extra['uid'],
                'addressnew': self.extra['token']
            }).encode('utf-8')).read().decode('ISO-8859-1')
        dom = pq(raw)
        self.name = dom('div').eq(1).text()
        availability = dom('div').eq(2).text().split(':')
        self.bikes = int(availability[1].lstrip())
        self.free = int(availability[2].lstrip())
        return self
