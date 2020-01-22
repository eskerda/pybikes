# -*- coding: utf-8 -*-
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Bicing(BikeShareSystem):
    meta = {
        'system': 'Bicing',
        'company': [
            'Barcelona de Serveis Municipals, S.A. (BSM)',
            'CESPA',
            'PBSC',
        ],
    }

    url = 'https://www.bicing.barcelona/get-stations'

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        self.stations = []

        data = json.loads(scraper.request(self.url))
        self.stations = [BicingStation(s) for s in data['stations']]


class BicingStation(BikeShareStation):

    def __init__(self, data):
        super(BicingStation, self).__init__()
        self.name = data['streetName']
        self.latitude = float(data['latitude'])
        self.longitude = float(data['longitude'])
        self.bikes = int(data['bikes'])
        self.free = int(data['slots'])
        self.extra = {
            'uid': int(data['id']),
            'online': data['status'] == 1,
            'has_ebikes': int(data['electrical_bikes'] > 0),
            'ebikes': int(data['electrical_bikes'])
        }
