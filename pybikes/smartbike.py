# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json
from lxml import html

from .base import BikeShareSystem, BikeShareStation
from . import utils

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
        if scraper is None:
            scraper = utils.PyBikesScraper()

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


class SmartShitty(BaseSystem):
    """
    BikeMI decided (again) to implement yet another way of displaying the map...

    """
    sync = True

    def __init__(self, tag, meta, feed_url):
        super(SmartShitty, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        page = scraper.request(self.feed_url)
        page_html=html.fromstring(page.encode('utf-8'))
        element = page_html.get_element_by_id("__NEXT_DATA__").text_content()
        element_string = element.encode('utf-8').decode("utf-8")
        raw_data = json.loads(element_string)
        stations_data = raw_data['props']['pageProps']['apolloState']
        stations = []

        for station_key in stations_data:
            station_data = stations_data[station_key]
            if station_data['__typename']=='DockGroup':
                stations.append(BikemiStation(station_data))
        self.stations = stations
        
class BikemiStation(BikeShareStation):
    def __init__(self, fields):
        name = fields['title']
        latitude = fields['coord']['lat']
        longitude = fields['coord']['lng']
        free = fields['availabilityInfo']['availableDocks']
        normal_bikes = fields['availabilityInfo']['availableVehicleCategories'][0]['count']
        ebikes_without_childseat = fields['availabilityInfo']['availableVehicleCategories'][1]['count']
        ebikes_with_childseat = fields['availabilityInfo']['availableVehicleCategories'][2]['count']
        extra = {
            'status': fields['state'],
            'uid': str(fields['id']),
            'address': fields['subTitle'],
            'online': fields['enabled'],
            'normal_bikes': normal_bikes,
            'ebikes_without_childseat': ebikes_without_childseat,
            'ebikes_with_childseat': ebikes_with_childseat,
            'ebikes': ebikes_without_childseat + ebikes_with_childseat
        }
       	bikes = normal_bikes + ebikes_without_childseat + ebikes_with_childseat
        super(BikemiStation, self).__init__(name, latitude, longitude, bikes, free, extra)
