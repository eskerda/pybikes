# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

try:
    # Python 2
    from HTMLParser import HTMLParser
except ImportError:
    # Python 3
    from html.parser import HTMLParser

from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Cyclocity','CyclocityStation','CyclocityWeb','CyclocityWebStation']

api_root = "https://api.jcdecaux.com/vls/v1/"

endpoints = {
    'contracts': 'contracts?apiKey={api_key}',
    'stations' : 'stations?apiKey={api_key}&contract={contract}',
    'station'  : 'stations/{station_id}?contract={contract}&apiKey={api_key}'
}

html_parser = HTMLParser()

class Cyclocity(BikeShareSystem):

    sync = True

    authed = True

    meta = {
        'system': 'Cyclocity',
        'company': ['JCDecaux'],
        'license': {
            'name': 'Open Licence',
            'url': 'https://developer.jcdecaux.com/#/opendata/licence'
        },
        'source': 'https://developer.jcdecaux.com'
    }

    def __init__(self, tag, meta, contract, key):
        super( Cyclocity, self).__init__(tag, meta)
        self.contract = contract
        self.api_key = key
        self.stations_url = api_root + endpoints['stations'].format(
            api_key  = self.api_key,
            contract = contract
        )
        self.station_url = api_root + endpoints['station'].format(
            api_key = self.api_key,
            contract = contract,
            station_id = '{station_id}' )

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        data = json.loads(scraper.request(self.stations_url))
        stations = []
        for info in data:
            try:
                station = CyclocityStation(info, self.station_url)
            except Exception:
                continue
            stations.append(station)
        self.stations = stations

    @staticmethod
    def get_contracts(api_key, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        url = api_root + endpoints['contracts'].format(api_key = api_key)
        return json.loads(scraper.request(url))


class CyclocityStation(BikeShareStation):

    def __init__(self, jcd_data, station_url):
        super(CyclocityStation, self).__init__()

        self.name      = jcd_data['name']
        self.latitude  = jcd_data['position']['lat']
        self.longitude = jcd_data['position']['lng']
        self.bikes     = jcd_data['available_bikes']
        self.free      = jcd_data['available_bike_stands']

        self.extra = {
            'uid': jcd_data['number'],
            'address': jcd_data['address'],
            'status': jcd_data['status'],
            'banking': jcd_data['banking'],
            'bonus': jcd_data['bonus'],
            'last_update': jcd_data['last_update'],
            'slots': jcd_data['bike_stands']
        }

        self.url = station_url.format(station_id = jcd_data['number'])

        if self.latitude is None or self.longitude is None:
            raise Exception('An station needs a lat/lng to be defined!')

    def update(self, scraper = None, net_update = False):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        super(CyclocityStation, self).update()

        if net_update:
            status = json.loads(scraper.request(self.url))
            self.__init__(status, self.url)
        return self

class CyclocityWeb(BikeShareSystem):
    sync = False

    meta = {
        'system': 'Cyclocity',
        'company': ['JCDecaux']
    }

    _list_url = '/service/carto'
    _station_url = '/service/stationdetails/{city}/{id}'

    def __init__(self, tag, meta, endpoint, city):
        super(CyclocityWeb, self).__init__(tag, meta)
        self.endpoint    = endpoint
        self.city        = city
        self.list_url    = endpoint + CyclocityWeb._list_url
        self.station_url = endpoint + CyclocityWeb._station_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        xml_markers = scraper.request(self.list_url)
        dom = etree.fromstring(xml_markers.encode('utf-7'))
        markers = dom.xpath('/carto/markers/marker')
        stations = []
        for marker in markers:
            station = CyclocityWebStation.from_xml(marker)
            station.url = self.station_url.format(
                city = self.city, id = station.extra['uid']
            )
            stations.append(station)
        self.stations = stations

class CyclocityWebStation(BikeShareStation):
    @staticmethod
    def from_xml(marker):
        station = CyclocityWebStation()
        station.name = marker.get('name').title()
        station.latitude  = float(marker.get('lat'))
        station.longitude = float(marker.get('lng'))

        station.extra = {
            'uid': int(marker.get('number')),
            'address': html_parser.unescape(
                marker.get('fullAddress').rstrip()
            ),
            'open': int(marker.get('open')) == 1,
            'bonus': int(marker.get('bonus')) == 1
        }
        return station

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        super(CyclocityWebStation, self).update()

        status_xml = scraper.request(self.url)
        status = etree.fromstring(status_xml.encode('utf-8'))

        self.bikes = int(status.findtext('available'))
        self.free  = int(status.findtext('free'))
        self.extra['open'] = int(status.findtext('open')) == 1
        self.extra['last_update'] = status.findtext('updated')
        self.extra['connected'] = status.findtext('connected')
        self.extra['slots'] = int(status.findtext('total'))
        self.extra['ticket'] = int(status.findtext('ticket')) == 1
