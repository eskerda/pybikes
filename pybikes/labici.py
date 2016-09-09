# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class LaBici(BikeShareSystem):

    meta = {
        'system': 'Labici',
        'company': ['Labici Bicicletas Públicas SL'],
    }

    base_url = 'http://labici.net/api-labici.php?module=parking&method=get-locations&city={city_code}'  # NOQA

    def __init__(self, tag, meta, city_code):
        super(LaBici, self).__init__(tag, meta)
        self.feed_url = self.base_url.format(city_code=city_code)

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        for item in data['data']:
            name = item['descripcion']
            latitude = float(item['latitude'])
            longitude = float(item['longitude'])
            bikes = int(item['xocupados'])
            free = int(item['libres'])
            extra = {
                'slots': item['num_puestos'],
                'uid': item['id_aparcamiento'],
            }
            station = BikeShareStation(name, latitude, longitude,
                                       bikes, free, extra)
            stations.append(station)

        self.stations = stations
