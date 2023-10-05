# -*- coding: utf-8 -*-
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.exceptions import InvalidStation
from pybikes.utils import filter_bounds

STATIONS_URL = '{endpoint}/get-stations'


class Bicing(BikeShareSystem):
    meta = {
        'ebikes': True,
    }

    def __init__(self, tag, meta, endpoint, bbox=None):
        super(Bicing, self).__init__(tag, meta)
        self.endpoint = endpoint
        self.bbox = bbox

    @property
    def stations_url(self):
        return STATIONS_URL.format(endpoint=self.endpoint)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.stations_url))
        stations = []
        for station_data in data['stations']:
            try:
                station = BicingStation(station_data)
            except InvalidStation:
                continue
            stations.append(station)

        if self.bbox:
            stations = list(filter_bounds(stations, None, self.bbox))

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
