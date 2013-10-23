# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json
from pyquery import PyQuery as pq

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['SmartBike', 'SmartBikeStation', \
           'SmartClunky', 'SmartClunkyStation'\
          ]

LAT_LNG_RGX = 'point \= new GLatLng\((.*?)\,(.*?)\)'
ID_ADD_RGX = 'idStation\=(.*)\&addressnew\=(.*)\&s\_id\_idioma'
ID_ADD_RGX_V = 'idStation\=\"\+(.*)\+\"\&addressnew\=(.*)\+\"\&s\_id\_idioma'

parse_methods = {
    'xml': 'get_xml_stations',
    'json': 'get_json_stations'
}

class BaseSystem(BikeShareSystem):
    meta = {
        'system': 'SmartBike',
        'company': 'ClearChannel'
    }

class SmartBike(BaseSystem):
    sync = True

    def __init__(self, tag, meta, feed_url, format = "json"):
        super(SmartBike, self).__init__(tag, meta)
        self.feed_url = feed_url
        if format not in parse_methods:
            raise Exception('Unsupported method %s' % format)
        self.method = parse_methods[format]

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        raw_req = scraper.request(self.feed_url)
        self.stations = eval(self.method)(self, raw_req)

def get_xml_stations(self, raw):
    raise Exception("Not implemented")

def get_json_stations(self, raw):
    # Double encoded json FTWTF..
    data = json.loads(json.loads(raw)[1]['data'])
    stations = map(SmartBikeStation, data)
    return stations

class SmartBikeStation(BikeShareStation):
    def __init__(self, info):
        super(SmartBikeStation, self).__init__(0)
        self.name      = info['StationName']
        self.bikes     = int(info['StationAvailableBikes'])
        self.free      = int(info['StationFreeSlot'])
        self.latitude  = float(info['AddressGmapsLatitude'])
        self.longitude = float(info['AddressGmapsLongitude'])
        self.extra = {
            'uid': info['StationID'],
            'status': info['StationStatusCode'],
            'districtCode': info['DisctrictCode'],
            'NearbyStationList': map(
                int, info['NearbyStationList'].split(',')
            )
        }

class SmartClunky(BaseSystem):
    sync = False
    list_url = "/localizaciones/localizaciones.php"
    station_url = "/CallWebService/StationBussinesStatus.php"

    def __init__(self, tag, meta, root_url, ** extra):
        super(SmartClunky, self).__init__(tag, meta)
        self.root_url = root_url
        if 'list_url' in extra:
            self.list_url = extra['list_url']

        if 'station_url' in extra:
            self.station_url = extra['station_url']

    def update(self, scraper = None):

        if scraper is None:
            scraper = utils.PyBikesScraper()

        raw = scraper.request(
            "{0}{1}".format(self.root_url, self.list_url)
        )
        geopoints = re.findall(LAT_LNG_RGX, raw)
        ids_addrs = re.findall(ID_ADD_RGX_V, raw)
        stations = []

        for index, geopoint in enumerate(geopoints):
            station = SmartClunkyStation(index)
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

class SmartClunkyStation(BikeShareStation):
    def update(self, scraper = None):

        if scraper is None:
            scraper = utils.PyBikesScraper()


        super(SmartClunkyStation, self).update()
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

