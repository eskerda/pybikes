# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class Velobike(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Velobike',
        'company': ['Velobike.kz, LLP', 'Smoove']
    }

    def __init__(self, tag, feed_url, meta):
        super(Velobike, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        # Each station is
        # {
        #     "id": "41",
        #     "code": "047",
        #     "name_ru": "047 Гостиница «Дипломат»",
        #     "name_en": "047 «Diplomat» hotel",
        #     "name_kz": "047 «Дипломат» қонақ үйі",
        #     "lat": "51.130769",
        #     "lng": "71.429361",
        #     "desc_ru": "",
        #     "desc_en": "",
        #     "desc_kz": "",
        #     "total_slots": "8",
        #     "free_slots": "8",
        #     "avl_bikes": "0",
        #     "address_ru": "На пересечении ул. Акмешеть, ул.Кунаева.",
        #     "address_kz": "Ақмешіт пен Қонаев көшелерінің қиылысында",
        #     "address_en": "At the intersection of Akmeshet str. and Kunaeva street",
        #     "is_deleted": "0",
        #     "is_hidden": "0",
        #     "is_sales": "0",
        #     "is_not_active": "0"
        # },
        for item in data:
            if item['is_deleted'] == '1':
                continue
            if item['is_hidden'] == '1':
                continue
            if item['is_sales'] == '1':
                continue
            if item['is_not_active'] == '1':
                continue
            name = item['name_ru']
            latitude = float(item['lat'])
            longitude = float(item['lng'])
            bikes = int(item['avl_bikes'])
            free = int(item['free_slots'])
            extra = {
                'uid': int(item['id']),
                'slots': int(item['total_slots']),
                'address': item['address_ru'],
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
