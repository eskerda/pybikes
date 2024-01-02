# -*- coding: utf-8 -*-
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded
from pybikes.exceptions import InvalidStation

STATIONS_URL = '{endpoint}/get-stations'


class Bicing(Bounded, BikeShareSystem):
    meta = {
        'ebikes': True,
    }

    def __init__(self, tag, meta, endpoint, bbox=None):
        super(Bicing, self).__init__(tag, meta, bounds=bbox)
        self.endpoint = endpoint

    @property
    def stations_url(self):
        return STATIONS_URL.format(endpoint=self.endpoint)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        # biki takes more than 30s to reply, increase it to at least 60s
        scraper.requests_timeout = max(scraper.requests_timeout, 600)
        data = json.loads(scraper.request(self.stations_url))

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
