# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class LaBici(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Labici',
        'company': 'labici.net',
        'country': 'Spain'
    }
    base_url = 'http://labici.net/api-labici.php?module=parking&method=get-locations&city={city_code}'

    def __init__(self, tag, meta):
        super(LaBici, self).__init__(tag, meta)
        self.feed_url =   self.base_url.format(city_code=meta['city_code'])

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url)
        )

        for item in data['data']:
            name = item['descripcion']
            latitude = float(item['latitude'])
            longitude = float(item['longitude'])
            bikes = int(item['num_puestos'])
            free = int(item['libres'])
            status = 'offline' if item['xactivo'] == '0' else 'online'
            extra = {
                'used_slots': item['ocupados'],
                'status': status
            }
            station = BikeShareStation(name, latitude, longitude,
                                       bikes, free, extra)
            stations.append(station)

        self.stations = stations
