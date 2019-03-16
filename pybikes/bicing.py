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

    name_format = u'{number} - {street} {street_number}'

    def __init__(self, data):
        super(BicingStation, self).__init__()
        self.name = self.name_format.format(
            number=data['id'],
            street=data['streetName'],
            street_number=data['streetNumber'],
        )
        self.latitude = float(data['latitude'])
        self.longitude = float(data['longitude'])
        self.bikes = int(data['bikes'])
        self.free = int(data['slots'])
        self.extra = {
            'uid': int(data['id']),
            'online': data['status'] == 1,
            'has_ebikes': 'ELECTRIC' in data['type'],
        }
