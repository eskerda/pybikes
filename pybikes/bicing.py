# -*- coding: utf-8 -*-
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.exceptions import InvalidStation


class Bicing(BikeShareSystem):
    meta = {
        'system': 'Bicing',
        'company': [
            'Barcelona de Serveis Municipals, S.A. (BSM)',
            'CESPA',
            'PBSC',
        ],
        'ebikes': True,
    }

    url = 'https://www.bicing.barcelona/get-stations'

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.url))
        stations = []
        for station_data in data['stations']:
            try:
                station = BicingStation(station_data)
            except InvalidStation:
                continue
            stations.append(station)
        self.stations = stations


class BicingStation(BikeShareStation):
    def __init__(self, data):
        super(BicingStation, self).__init__()
        self.name = data['streetName']

        try:
            self.latitude = float(data['latitude'])
            self.longitude = float(data['longitude'])
        except ValueError:
            raise InvalidStation

        self.bikes = int(data['bikes'])
        self.free = int(data['slots'])
        self.extra = {
            'uid': int(data['id']),
            'online': data['status'] == 1,
        }

        if 'mechanical_bikes' in data:
            self.extra['normal_bikes'] = int(data['mechanical_bikes'])

        if 'electrical_bikes' in data:
            self.extra['has_ebikes'] = True
            self.extra['ebikes'] = int(data['electrical_bikes'])
