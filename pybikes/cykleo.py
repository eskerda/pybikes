# -*- coding: utf-8 -*-
# Copyright (C) 2010-2023, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


BASE_URL = 'https://portail.cykleo.fr/pu/stations/availability?organization_id={organization}'


class Cykleo(BikeShareSystem):

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2',
        'Referer':'https://portail.cykleo.fr/',
        'Authority': 'portail.cykleo.fr',
    }

    meta = {
        'system': 'Cykleo',
        'company': ['Cykleo SAS']
    }

    def __init__(self, tag, meta, organization):
        super(Cykleo, self).__init__(tag, meta)
        self.url = BASE_URL.format(organization=organization)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        places = json.loads(scraper.request(self.url, method='GET', headers=Cykleo.headers, ssl_verification=False))
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

        normal_bikes = station['availableClassicBikeCount']
        e_bikes = station['availableElectricBikeCount']

        self.bikes = normal_bikes + e_bikes
        self.free = station['availableDockCount']

        self.extra = {
            'uid': station['id'],
            'number': asset_station['commercialNumber'],
            'ebikes': e_bikes,
            'normal_bikes': normal_bikes,
            'online': station_details['status'] == 'IN_SERVICE',
            'status': station_details['status']
        }
