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
        'license': 'https://creativecommons.org/licenses/by/4.0/',
        'source': 'http://opendata-ajuntament.barcelona.cat/data/en/dataset/bicing',
    }

    url = 'http://wservice.viabicing.cat/v2/stations'

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
            'altitude': data['altitude'],
            'status': data['status'],
            # We keep this shitty name because of compatibility with the old
            # feed
            'NearbyStationList': [
                int(uid.strip()) for uid in data['nearbyStations'].split(',')
            ],
            'has_ebikes': 'ELECTRIC' in data['type'],
        }
