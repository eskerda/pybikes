# -*- coding: utf-8 -*-
# Copyright (C) 2015, Ben Caller <bcaller@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from lxml import html
from lxml.cssselect import CSSSelector

from .base import BikeShareSystem, BikeShareStation
from . import utils
from contrib import TSTCache

__all__ = ['GoBike', 'GoBikeStation']

PAGE_SIZE = 10
STATION_LIST_PATH = '/umbraco/Surface/BookingSurface/GetStationsList'

cache = TSTCache(delta=60)

class GoBike(BikeShareSystem):
    sync = True

    meta = {
        'system': 'GoBike',
        'company': 'GoBike'
    }

    def __init__(self, tag, meta, url, availability_path):
        super(GoBike, self).__init__(tag, meta)
        self.url = url
        self.availability_path = availability_path

    def _get_availability_request(self, page, number_of_stations):
        url = self.url + self.availability_path
        data = {
            'lat': self.meta['latitude'],
            'lng': self.meta['longitude']
        }
        if number_of_stations <= PAGE_SIZE:
            return url, 'POST', data

        data['page'] = page
        # The query string is not really necessary, but is added to help with the caching
        return '{}?p={}'.format(url, page), 'POST', data

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper(cache)

        station_list = json.loads(scraper.request(self.url + STATION_LIST_PATH))["List"]
        stations_by_id = dict((str(s["UnifiedId"]), GoBikeStation(s)) for s in station_list)

        station_selector = CSSSelector('.span6 .station-basicinfo')
        available_selector = CSSSelector('.station-availablebikes')
        # Can only query 10 stations per request, perhaps we should do this async
        for page in range(0, len(station_list)/PAGE_SIZE + (len(station_list) % PAGE_SIZE > 0)):
            body = scraper.request(*self._get_availability_request(page, len(station_list)))
            dom = html.fromstring(body)
            for e in station_selector(dom):
                uid = e.get('id').split('_')[1]
                bikes = int(available_selector(e)[0].text)
                stations_by_id[uid].set_available_bikes(bikes)

        self.stations = stations_by_id.values()


class GoBikeStation(BikeShareStation):
    def __init__(self, info):
        super(GoBikeStation, self).__init__()
        location = info['Location']
        self.name = info['Name']
        self.latitude = float(location['Latitude'])
        self.longitude = float(location['Longitude'])
        self.extra = {
            'uid': int(info['UnifiedId']),
            'street': location['Street'],
            'street_building_identifier': location['StreetBuildingIdentifier'],
            'district': location['DistrictName'],
            'city': location['City'],
            'zip': location['ZipCode'],
            'status': int(info['Status']),
            'address': None
        }

        # Unnecessary nice address but I added it because DisplayName is backwards
        if self.extra['street']:
            self.extra['address'] = self.extra['street']
            if self.extra['street_building_identifier']:
                self.extra['address'] += ' ' + self.extra['street_building_identifier']  # Number comes after in DK
            if self.extra['district']:
                self.extra['address'] += ', ' + self.extra['district']
            if self.extra['zip']:
                self.extra['address'] += ', ' + self.extra['zip']
                if self.extra['city']:
                    self.extra['address'] += ' ' + self.extra['city']
            elif self.extra['city']:
                self.extra['address'] += ', ' + self.extra['city']

    def set_available_bikes(self, n):
        self.bikes = n
        # self.free is unavailable, but with this system you can lock the bike next to a full station
