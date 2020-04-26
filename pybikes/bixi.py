# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
import codecs

from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['BixiSystem', 'BixiStation']

parse_methods = {
    'xml': 'get_xml_stations',
    'json': 'get_json_stations',
    'json_from_xml': 'get_json_xml_stations'
}

class BixiSystem(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Bixi',
        'company': ['PBSC']
    }

    def __init__(self, tag, feed_url, meta, format):
        super( BixiSystem, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.method = format

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        if self.method not in parse_methods:
            raise Exception(
                'Extractor for method %s is not implemented' % self.method )

        self.stations = eval(parse_methods[self.method])(self, scraper)

def get_xml_stations(self, scraper):
    xml_data = scraper.request(self.feed_url)
    dom = etree.fromstring(xml_data.encode('utf-8'))
    markers = dom.xpath('/stations/station')
    return list(map(BixiStation.from_xml, markers))

def get_json_stations(self, scraper):
    data = json.loads(scraper.request(self.feed_url))
    stations = []
    for marker in data['stationBeanList']:
        try:
            station = BixiStation.from_json(marker)
        except exceptions.StationPlannedException:
            continue
        stations.append(station)
    return stations

def get_json_xml_stations(self, scraper):
    raw = scraper.request(self.feed_url).decode('unicode-escape')
    data = json.loads(raw)
    return list(map(BixiStation.from_json_xml, data))

class BixiStation(BikeShareStation):
    def __init__(self):
        super(BixiStation, self).__init__()

    @staticmethod
    def from_xml(xml_data):
        """ xml marker object as in
        <station>
            <id>1</id>
            <name>Notre Dame / Place Jacques Cartier</name>
            <terminalName>6001</terminalName>
            <lat>45.508183</lat>
            <long>-73.554094</long>
            <installed>true</installed>
            <locked>false</locked>
            <installDate>1276012920000</installDate>
            <removalDate />
            <temporary>false</temporary>
            <nbBikes>14</nbBikes>
            <nbEmptyDocks>17</nbEmptyDocks>
        </station>
        """
        station = BixiStation()
        terminalName = xml_data.findtext('terminalName')
        name = xml_data.findtext('name')
        latestUpdateTime = xml_data.findtext('latestUpdateTime')

        station.name = "%s - %s" % (terminalName, name)
        station.latitude = float(xml_data.findtext('lat'))
        station.longitude = float(xml_data.findtext('long'))
        station.bikes = int(xml_data.findtext('nbBikes'))
        station.free = int(xml_data.findtext('nbEmptyDocks'))

        station.extra = {
            'uid': int(xml_data.findtext('id')),
            'name': name,
            'terminalName' : terminalName,
            'locked': utils.str2bool(xml_data.findtext('locked')),
            'installed': utils.str2bool(xml_data.findtext('installed')),
            'temporary': utils.str2bool(xml_data.findtext('temporary')),
            'installDate': xml_data.findtext('installDate'),
            'removalDate': xml_data.findtext('removalDate')
        }

        if latestUpdateTime is not None and latestUpdateTime != '0':
            station.extra['latestUpdateTime'] = latestUpdateTime

        return station

    @staticmethod
    def from_json(data):
        '''
          {
            "id":2026,
            "stationName":"Broadway & W 60 Street",
            "availableDocks":0,
            "totalDocks":0,
            "latitude":40.76915505,
            "longitude":-73.98191841,
            "statusValue":"Planned",
            "statusKey":2,
            "availableBikes":0,
            "stAddress1":"Broadway & W 60 Street",
            "stAddress2":"",
            "city":"",
            "postalCode":"",
            "location":"",
            "altitude":"",
            "testStation":false,
            "lastCommunicationTime":null,
            "landMark":""
          }
        '''
        station = BixiStation()
        if data['statusValue'] == 'Planned' or data['testStation']:
            raise exceptions.StationPlannedException()

        station.name      = "%s - %s" % (data['id'], data['stationName'])
        station.longitude = float(data['longitude'])
        station.latitude  = float(data['latitude'])
        station.bikes     = int(data['availableBikes'])
        station.free      = int(data['availableDocks'])

        station.extra = {
            'uid': int(data['id']),
            'statusValue': data['statusValue'],
            'statusKey': data['statusKey'],
            'stAddress1': data['stAddress1'],
            'stAddress2': data['stAddress2'],
            'city': data['city'],
            'postalCode': data['postalCode'],
            'location': data['location'],
            'altitude': data['altitude'],
            'testStation': data['testStation'],
            'lastCommunicationTime': data['lastCommunicationTime'],
            'landMark': data['landMark'],
            'totalDocks': data['totalDocks']
        }

        return station

    @staticmethod
    def from_json_xml(data):
        """ json marker object translated from xml
        {
            "id": "2",
            "name": "Docklands Drive - Docklands",
            "terminalName": "60000",
            "lastCommWithServer": "1375644471147",
            "lat": "-37.814022",
            "long": "144.939521",
            "installed": "true",
            "locked": "false",
            "installDate": "1313724600000",
            "removalDate": {  },
            "temporary": "false",
            "public": "true",
            "nbBikes": "15",
            "nbEmptyDocks": "8",
            "latestUpdateTime": "1375592453128"
        }
        """

        station = BixiStation()

        station.name = "%s - %s" % (data['terminalName'], data['name'])
        station.latitude = float(data['lat'])
        station.longitude = float(data['long'])
        station.bikes = int(data['nbBikes'])
        station.free = int(data['nbEmptyDocks'])

        station.extra = {
            'uid': int(data['id']),
            'name': data['name'],
            'terminalName': data['terminalName'],
            'lastCommWithServer': data['lastCommWithServer'],
            'installed': utils.str2bool(data['installed']),
            'locked': utils.str2bool(data['locked']),
            'installDate': data['installDate'],
            'removalDate': data['removalDate'],
            'temporary': utils.str2bool(data['temporary']),
            'public': utils.str2bool(data['public']),
            'latestUpdateTime': data['latestUpdateTime']
        }
        return station
