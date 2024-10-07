# -*- coding: utf-8 -*-
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


class FifteenAPI(Bounded, BikeShareSystem):

    sync = True

    meta = {
        'system': 'Fifteen',
        'company': ['Fifteen SAS']
    }

    def __init__(self, tag, feed_url, meta, bbox=None):
        super(FifteenAPI, self).__init__(tag, meta, bounds=bbox)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        response = json.loads(scraper.request(self.feed_url))
        stations = []

        if isinstance(response, dict):
            if response['statusCode'] != 200:
                raise Exception('response status: %d' % response['statusCode'])
            data = response['data']['stations']
        else:
            data = response

        for s in data:
            lat = float(s['coordinates'][1])
            lng = float(s['coordinates'][0])
            name = s['label']
            bikes = int(s['availableBikes'])
            slots = int(s['availableSlots'])

            extra = {
                'uid': s['id'],
                'online': not s['isClosed'],
            }

            station = BikeShareStation(name, lat, lng, bikes, slots, extra)
            stations.append(station)

        self.stations = stations
