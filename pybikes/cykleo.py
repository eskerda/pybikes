# -*- coding: utf-8 -*-
# Copyright (C) 2010-2022, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from .base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper, filter_bounds
from pybikes.contrib import TSTCache

__all__ = ['Cykleo', 'CykleoStation']

BASE_URL = 'https://{hostname}/pu/stations/availability?organization_id={organization}&get_biketypes=1'

# Since most networks share the same hostname, there's no need to keep hitting
# the endpoint on the same urls. This caches the feed for 60s
cache = TSTCache(delta=60)


class Cykleo(BikeShareSystem):
    sync = True #TODO: remove??
    unifeed = False

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2',
        'DNT':'1',
        'Referer':'https://portail.cykleo.fr/'
    }

    meta = {
        'system': 'Cykleo',
        'company': ['Cykleo SAS']
    }

    def __init__(self, tag, meta, organization, hostname='portail.cykleo.fr',
                 bbox=None):
        super(Cykleo, self).__init__(tag, meta)
        self.url = BASE_URL.format(hostname=hostname, organization=organization)
        self.organization = organization
        self.bbox = bbox

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper(cache)
        
        places = json.loads(str(scraper.request(self.url, method='GET', headers=Cykleo.headers)))

        # We want to raise an error if a 'organization' is invalid, right?
        assert places, f"Not found: cykleo organization '{self.organization}'"

        if self.bbox:
            def getter(station):
                station_coords = station['station']['assetStation']['coordinate']
                lat, lng = station_coords['y'], station_coords['x']
                return (float(lat), float(lng))
            places = filter_bounds(places, getter, self.bbox)
        
        self.stations = list(map(CykleoStation, places))


class CykleoStation(BikeShareStation):
    def __init__(self, station):
        super(CykleoStation, self).__init__()
        
        station_details = station['station']
        asset_station = station_details['assetStation']
        station_coords = asset_station['coordinate']

        self.name = asset_station['commercialName']
        self.latitude = float(station_coords['y'])
        self.longitude = float(station_coords['x'])

        self.extra = {}

        self.extra['uid'] = station['id']

        if 'commercialNumber' in asset_station:
            self.extra['number'] = asset_station['commercialNumber']

        if 'address' in asset_station:
            self.extra['address'] = ''
            if 'line1' in asset_station['address']:
                self.extra['address'] += str(asset_station['address']['line1']).strip()
            if 'line2' in asset_station['address']:
                self.extra['address'] += ' ' + str(asset_station['address']['line2']).strip()
                self.extra['address'] = str(self.extra['address']).strip()
            if 'line3' in asset_station['address']:
                self.extra['address'] += ' ' + str(asset_station['address']['line3']).strip()
                self.extra['address'] = str(self.extra['address']).strip()
            if 'line4' in asset_station['address']:
                self.extra['address'] += ' ' + str(asset_station['address']['line4']).strip()
                self.extra['address'] = str(self.extra['address']).strip()
            if 'postalCode' in asset_station['address']:
                self.extra['address'] += ', ' + str(asset_station['address']['postalCode']).strip()
                self.extra['address'] = str(self.extra['address']).strip()
            if 'city' in asset_station['address']:
                self.extra['address'] += ' ' + str(asset_station['address']['city']).lower().capitalize().strip()

            self.extra['address'] = re.sub(r'( ){2}( )*',' ',str(self.extra['address']).strip())

        self.bikes = 0
        self.free = 0
        self.extra['slots'] = 0

        if 'availableClassicBikeCount' in station:
            self.extra['classic_bikes'] = int(station['availableClassicBikeCount'])
            self.free += self.extra['classic_bikes']
        
        if 'availableElectricBikeCount' in station:
            self.extra['electric_bikes'] = int(station['availableElectricBikeCount'])
            self.bikes += self.extra['classic_bikes']
        
        # only available bikes and slots are given
        self.bikes = self.free

        if 'availableDockCount' in station:
            self.extra['slots'] = int(station['availableDockCount'])
