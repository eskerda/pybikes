# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
import codecs

from pyquery import PyQuery as pq

from .base import BikeShareSystem, BikeShareStation
from . import utils

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
        'company': 'PBSC' 
    }

    def __init__(self, tag, feed_url, meta, format):
        super( BixiSystem, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.method = format

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        if self.method not in parse_methods:
            raise Exception('Extractor for method %s is not implemented' % self.method )

        self.stations = eval(parse_methods[self.method])(self, scraper)

def get_xml_stations(self, scraper):
    xml_data = scraper.request(self.feed_url)
    dom = pq(xml_data.encode('utf-8'), parser = 'xml')
    markers = dom('station')
    stations = []
    
    for index, marker in enumerate(markers):
        station = BixiStation(index)
        station.from_xml(marker)
        stations.append(station)
    return stations

def get_json_stations(self, scraper):
    data = json.loads(scraper.request(self.feed_url))
    stations = []
    index = 0
    for marker in data['stationBeanList']:
        try:
          station = BixiStation(index)
          station.from_json(marker)
          index = index + 1
          stations.append(station)
        except Exception as e:
          print e
    return stations

def get_json_xml_stations(self, scraper):
    raw = scraper.request(self.feed_url).decode('unicode-escape')
    data = json.loads(raw)
    stations = []
    for index, marker in enumerate(data):
        station = BixiStation(index)
        station.from_json_xml(marker)
        stations.append(station)
    return stations

class BixiStation(BikeShareStation):

    def from_xml(self, xml_data):
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
        xml_data = pq(xml_data, parser='xml')
        
        terminalName = xml_data('terminalName').text()
        name = xml_data('name').text()
        self.name = "%s - %s" % (terminalName, name)
        self.latitude = float(xml_data('lat').text())
        self.longitude = float(xml_data('long').text())
        self.bikes = int(xml_data('nbBikes').text())
        self.free = int(xml_data('nbEmptyDocks').text())

        self.extra = {
            'uid': int(xml_data('id').text()),
            'name': name,
            'terminalName' : terminalName,
            'locked': utils.str2bool(xml_data('locked').text()),
            'installed': utils.str2bool(xml_data('installed').text()),
            'temporary': utils.str2bool(xml_data('temporary').text()),
            'installDate': xml_data('installDate').text(),
            'removalDate': xml_data('removalDate').text(),
            'latestUpdateTime': xml_data('latestUpdateTime').text()
        }
        return self

    def from_json(self, data):
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

        if data['statusValue'] == 'Planned' or data['testStation']:
            raise Exception('Station is only Planned or is a Test one')

        self.name      = "%s - %s" % (data['id'], data['stationName'])
        self.longitude = float(data['longitude'])
        self.latitude  = float(data['latitude'])
        self.bikes     = int(data['availableBikes'])
        self.free      = int(data['availableDocks'])

        self.extra = {
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

        return self
    def from_json_xml(self, data):
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
        
        self.name = "%s - %s" % (data['terminalName'], data['name'])
        self.latitude = float(data['lat'])
        self.longitude = float(data['long'])
        self.bikes = int(data['nbBikes'])
        self.free = int(data['nbEmptyDocks'])

        self.extra = {
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
        return self