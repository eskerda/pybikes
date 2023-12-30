# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json
from lxml import html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


LAT_LNG_RGX = 'point \= new GLatLng\((.*?)\,(.*?)\)'
ID_ADD_RGX = 'idStation\=(.*)\&addressnew\=(.*)\&s\_id\_idioma'
ID_ADD_RGX_V = 'idStation\=\"\+(.*)\+\"\&addressnew\=(.*)\+\"\&s\_id\_idioma'

parse_methods = {
    'xml': 'get_xml_stations',
    'json': 'get_json_stations',
    'json_v2': 'get_json_v2_stations'
}


class BaseSystem(BikeShareSystem):
    meta = {
        'system': 'SmartBike',
        'company': ['ClearChannel']
    }


class SmartBike(BaseSystem):
    sync = True

    def __init__(self, tag, meta, feed_url, format="json"):
        super(SmartBike, self).__init__(tag, meta)
        self.feed_url = feed_url
        if format not in parse_methods:
            raise Exception('Unsupported method %s' % format)
        self.method = parse_methods[format]

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        raw_req = scraper.request(self.feed_url)
        self.stations = eval(self.method)(self, raw_req)


def get_xml_stations(self, raw):
    raise Exception("Not implemented")


def get_json_stations(self, raw):
    # Double encoded json FTWTF..
    data = json.loads(json.loads(raw)[1]['data'])
    stations = list(map(SmartBikeStation, data))
    return stations


def get_json_v2_stations(self, raw):
    data = json.loads(raw)
    stations = list(map(SmartBikeStation, data))
    return stations


class SmartBikeStation(BikeShareStation):
    def __init__(self, info):
        super(SmartBikeStation, self).__init__()
        try:
            self.name = info['StationName']
            self.bikes = int(info['StationAvailableBikes'])
            self.free = int(info['StationFreeSlot'])
            self.latitude = float(info['AddressGmapsLatitude'])
            self.longitude = float(info['AddressGmapsLongitude'])
            self.extra = {
                'uid': int(info['StationID']),
                'status': info['StationStatusCode'],
                'districtCode': info['DisctrictCode'],
                'NearbyStationList': list(map(
                    int, info['NearbyStationList'].split(',')
                ))
            }
        except KeyError:
            # Either something has changed, or it's the other type of feed
            # Same data, different keys.
            self.name = info['name']
            self.bikes = int(info['bikes'])
            self.free = int(info['slots'])
            self.latitude = float(info['lat'])
            self.longitude = float(info['lon'])
            self.extra = {
                'uid': int(info['id']),
                'status': info['status']
            }
            if 'address' in info:
                self.extra['address'] = info['address']
            if 'district' in info:
                self.extra['districtCode'] = info['district']
            elif 'districtCode' in info:
                self.extra['districtCode'] = info['districtCode']

            nearby_stations = info.get('nearbyStations')
            if nearby_stations and nearby_stations != "0":
                self.extra['NearbyStationList'] = list(map(
                    int, nearby_stations.split(',')
                ))

            if 'zip' in info and info['zip']:
                self.extra['zip'] = info['zip']

            if 'stationType' in info and \
                    info['stationType'] == 'ELECTRIC_BIKE':
                self.extra['ebikes'] = True


class SmartBike2(BaseSystem):

    def __init__(self, tag, meta, endpoint):
        super(SmartBike2, self).__init__(tag, meta)

        self.stations_url = endpoint + '/station_list.json'
        self.stations_status_url = endpoint + '/station_status_list.json'


    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations = json.loads(scraper.request(self.stations_url))
        statuses = json.loads(scraper.request(self.stations_status_url))

        self.stations = list(map(lambda z: SmartBike2Station(*z), zip(stations, statuses)))


class SmartBike2Station(BikeShareStation):
    def __init__(self, info, status):
        assert info['id'] == status['id'], "info and status are non consecutive, fix your code"

        name = info['name']
        latitude = float(info['location']['lat'])
        longitude = float(info['location']['lon'])
        bikes = int(status['availability']['bikes'])
        free = int(status['availability']['slots'])
        extra = {
            'status': status['status'],
            'uid': int(info['id']),
            'address': info['address'],
        }

        super(SmartBike2Station, self).__init__(name, latitude, longitude, bikes, free, extra)
