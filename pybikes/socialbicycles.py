# -*- coding: utf-8 -*-

import json

from pybikes import BikeShareStation, BikeShareSystem
from pybikes.utils import PyBikesScraper

BASE_URL = 'https://app.socialbicycles.com/api/networks/{uid}/hubs?page={page}&per_page='


class SocialBicycles(BikeShareSystem):
    sync = True
    unifeed = True
    meta = {'system': 'SocialBicycles', 'company': ['Social Bicycles Inc.']}

    def __init__(self, tag, uid, meta, referer='https://map-cdn.socialbicycles.com', page_size=999):
        super(SocialBicycles, self).__init__(tag, meta)
        self.uid = uid
        self.headers = {}
        self.page_size = page_size

        if referer:
            self.headers = {'Referer': referer}

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()

        scraper.headers.update(self.headers)

        page = 1
        places = []
        while page:
            resp = scraper.request(
                BASE_URL.format(uid=self.uid, page=page) + str(self.page_size)
            )
            data = json.loads(resp)
            if page * self.page_size > data['total_entries']:
                page = 0
            else:
                page += 1

            places.extend(data['items'])

        self.stations = list(map(SocialBicyclesStation, places))


class SocialBicyclesStation(BikeShareStation):
    def __init__(self, place):
        super(SocialBicyclesStation, self).__init__()
        self.name = place['name']
        self.bikes = place['available_bikes']
        self.free = place['free_racks']

        coordinates = place['middle_point']['coordinates']
        (self.longitude, self.latitude) = coordinates

        self.extra = {}
        self.extra['uid'] = place['id']
        self.extra['slots'] = place['racks_amount']
