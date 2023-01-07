# -*- coding: utf-8 -*-

import re
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

# Each station is formatted as:
# {
#   "id": "cecqdqutu70fusn3jor0",
#   "type": 2,
#   "product_type": 2,
#   "entity_type": 0,
#   "info": {
#     "bike_autonomy": 19600,
#     "number_of_bikes": 10,
#     "bike_state_of_charge": 69
#   },
#   "location": {
#     "type": "Point",
#     "coordinates": [
#       5.38209613,
#       43.24693037
#     ]
#   },
#   "label": "Lapin Blanc",
#   "parent_id": "ce4bhih2rcd13ifvqfr0",
#   "distance": 5607.314337868474
# }
# Extracted from :https://levelo.ampmetropole.fr/api/stations at Marseille, France


class FifteenAPI(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Fifteen',
        'company': ['Fifteen SAS']
    }

    def __init__(self, tag, feed_url, meta):
        super(FifteenAPI, self).__init__(tag, meta)
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

        seen_ids = set()

        for s in data:
            # dedupe by parent_id
            if s['parent_id'] in seen_ids:
                continue
            seen_ids.add(s['parent_id'])

            lat = float(s['location']['coordinates'][0])
            lng = float(s['location']['coordinates'][1])
            name = s['label']
            bikes = int(s['info']['number_of_bikes'])

            extra = {
                'bike_state_of_charge': int(s['info'].get('bike_state_of_charge', 0)),
                'bike_autonomy': int(s['info']['bike_autonomy']),
                'uid': s['parent_id'],
                'distance' : int(s['distance']),
            }

            station = BikeShareStation(name, lat, lng, bikes, None, extra)
            stations.append(station)

        self.stations = stations
