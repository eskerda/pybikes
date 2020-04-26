# -*- coding: utf-8 -*-
# Copyright (C) 2015, Ben Caller <bcaller@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import json
try:
    # Python 2
    from urlparse import urljoin
except ImportError:
    # Python 3
    from urllib.parse import urljoin

from lxml import html, etree
from lxml.cssselect import CSSSelector

from . import utils
from .base import BikeShareSystem, BikeShareStation

# The number of free slots is unavailable
# However, you can lock the bike next to any full station

PAGE_SIZE = 10
STATION_LIST_PATH = '/umbraco/Surface/BookingSurface/GetStationsList'


class GoBike(BikeShareSystem):
    sync = True

    meta = {
        'system': 'GoBike',
        'company': ['Gobike A/S']
    }

    def __init__(self, tag, meta, hostname, availability_path):
        super(GoBike, self).__init__(tag, meta)
        self.availability_url = urljoin(hostname, availability_path)
        self.stations_url = urljoin(hostname, STATION_LIST_PATH)

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()

        # Request station names and locations from JSON file
        stations = json.loads(scraper.request(self.stations_url))["List"]
        stations_by_id = {
            str(s["UnifiedId"]): GoBikeStation(s) for s in stations
        }

        # Request number of bikes, at 10 stations per page
        for page in self._get_all_pages(scraper, len(stations)):
            for uid, bikes in self._parse_page(page):
                stations_by_id[uid].bikes = bikes

        self.stations = list(stations_by_id.values())

    def _get_all_pages(self, scraper, n_stations):
        n_pages = n_stations/PAGE_SIZE + (n_stations % PAGE_SIZE > 0)
        for p in range(0, int(n_pages)):
            data = {
                'lat': self.meta['latitude'],
                'lng': self.meta['longitude'],
                'page': p
            }
            yield scraper.request(self.availability_url, 'POST', data=data)

    @staticmethod
    def _parse_page(body):
        station_selector = CSSSelector('.span6 .station-basicinfo')
        available_selector = CSSSelector('.station-availablebikes')
        dom = html.fromstring(body)
        for station in station_selector(dom):
            uid = station.get('id').split('_')[1]
            bikes = int(available_selector(station)[0].text)
            yield uid, bikes


class GoBikeStation(BikeShareStation):
    def __init__(self, info):
        super(GoBikeStation, self).__init__()
        location = info['Location']
        self.name = info['Name']
        self.latitude = float(location['Latitude'])
        self.longitude = float(location['Longitude'])
        self.extra = {
            'uid': int(info['UnifiedId']),
            'status': int(info['Status']),
            'altitude': int(location['Altitude']),
            'address': GoBikeStation._format_address(location)
        }

    @staticmethod
    def _format_address(location):
        address_sections = [
            ['Street', 'StreetBuildingIdentifier'],
            ['DistrictName'],
            ['ZipCode', 'City'],
        ]
        address = []
        for section in address_sections:
            components = filter(None, (location.get(k) for k in section))
            part = ' '.join(components)
            address.append(part)
        address = filter(None, address)
        address = ', '.join(address)

        return address


class GoBikeXML(BikeShareSystem):
    meta = {
        'system': 'GoBike',
        'company': ['Gobike A/S'],
    }

    def __init__(self, tag, meta, feed_url):
        super(GoBikeXML, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()
        xml_stations = scraper.request(self.feed_url).encode('utf8')
        stations = etree.fromstring(xml_stations).xpath('//DockingStation')
        self.stations = list(map(GoBikeXMLStation, stations))


class GoBikeXMLStation(BikeShareStation):
    def __init__(self, dom):
        super(GoBikeXMLStation, self).__init__()
        self.name = dom.findtext('DockingStationName')
        self.latitude = float(dom.findtext('Latitude'))
        self.longitude = float(dom.findtext('Longitude'))
        self.bikes = int(dom.findtext('FreeBikes'))
        self.free = int(dom.findtext('FreeDockingPoints'))
        self.extra['uid'] = int(dom.findtext('DockingStationId'))
        self.extra['slots'] = int(dom.findtext('DockingPoints'))
