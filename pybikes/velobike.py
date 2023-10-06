# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class Velobike(BikeShareSystem):

    sync = True

    company = ['Smoove']

    def __init__(self, tag, feed_url, meta):
        meta['company'] += Velobike.company
        super(Velobike, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))

        # Some feeds have it inside a list, others within `data`
        if isinstance(data, dict):
            data = data.get('data') or data.get('response')

        for item in data:
            if 'is_deleted' in item and item['is_deleted'] == '1':
                continue
            if 'is_hidden' in item and item['is_hidden'] == '1':
                continue
            if 'is_sales' in item and item['is_sales'] == '1':
                continue
            if 'is_not_active' in item and item['is_not_active'] == '1':
                continue

            name = item.get('name_ru') or item.get('name')
            latitude = item.get('lat') or item.get('coordinates')[0]
            longitude = item.get('lng') or item.get('coordinates')[1]
            latitude = float(latitude)
            longitude = float(longitude)
            bikes = int(item['avl_bikes'])
            free = int(item['free_slots'])
            extra = {
                'uid': item.get('id') or item.get('nid'), 
                'slots': int(item['total_slots'])
            }
            extra['uid'] = int(extra['uid'])

            if 'address_ru' in item:
                extra['address'] = item['address_ru']

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
