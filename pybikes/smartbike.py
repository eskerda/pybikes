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
        'company': 'ClearChannel'
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
    stations = map(SmartBikeStation, data)
    return stations


def get_json_v2_stations(self, raw):
    data = json.loads(raw)
    stations = map(SmartBikeStation, data)
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
                'NearbyStationList': map(
                    int, info['NearbyStationList'].split(',')
                )
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
                self.extra['NearbyStationList'] = map(
                    int, nearby_stations.split(',')
                )

            if 'zip' in info and info['zip']:
                self.extra['zip'] = info['zip']

            if 'stationType' in info and \
                    info['stationType'] == 'ELECTRIC_BIKE':
                self.extra['ebikes'] = True


class SmartShitty(BaseSystem):
    """
    BikeMI decided (again) to implement yet another way of displaying the map...
    This time the data come in a less messy way in comparison to the previous version,
    but the HTML comes unescaped (escaped bellow for better understanding).
    Who the fuck pay this guys money, seriously?

    GoogleMap.addMarker(
        '/media/assets/images/station_map/more_than_five_bikes_flag.png',
        45.464683238626,
        9.18879747390747,
        'Duomo',
        '<div style="width: 240px; height: 120px;">
            <span style="font-weight: bold;">178 - V Alpini</span>
            <br>
            <ul>
                <li>Available bicycles: 9</li>
                <li>Available electrical bicycles: 0</li>
                <li>Available slots: 20</li>
                </ul>
        </div>');
    """
    sync = True

    RGX_MARKERS = r'GoogleMap\.addMarker\(.*?,\s*(\d+.\d+)\s*,\s*(\d+.\d+),\s*\'(.*?)\',(.*?)\)\;'

    def __init__(self, tag, meta, feed_url):
        super(SmartShitty, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        page = scraper.request(self.feed_url)
        stations_data = re.findall(SmartShitty.RGX_MARKERS,
                                   page.encode('utf-8'))
        stations = []
        stats_query = """
            //td[span[text() = "%s"]]/
                following-sibling::td/text()
        """

        stats_rules = {
            'std': 'Bicycles',
            'ebikes': 'Electric bicycles',
            # Kids bikes seem to not be implemented
            # 'kids_bikes': 'Bicycles for kids'
        }

        for station_data in stations_data:
            latitude, longitude, name, mess = station_data
            html_mess = html.fromstring(mess.decode('unicode_escape'))
            stats = {}
            bikes = 0
            extra = {}

            for k, rule in stats_rules.iteritems():
                stats[k] = map(int, html_mess.xpath(stats_query % rule))

            if stats['std']:
                bikes += stats['std'][0]
                free = stats['std'][1]

            if stats['ebikes'] and stats['ebikes'][0] > 0:
                bikes += stats['ebikes'][0]
                extra['ebikes'] = stats['ebikes'][0]
                extra['has_ebikes'] = True

            station = BikeShareStation(name, float(latitude), float(longitude),
                                       bikes, free, extra)
            stations.append(station)
        self.stations = stations
