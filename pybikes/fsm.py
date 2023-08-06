# -*- coding: utf-8 -*-
# Copyright (C) 2017, aronsky <aronsky@gmail.com>
# Copyright (C) 2023, eskerda <eskerda@gmail.com>

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


ENDPOINT = "https://www.tel-o-fun.co.il/api/privatearea/v1"
STATIONS_URL = ENDPOINT + "/map"
STATION_INFO_URL = ENDPOINT + "/station/{uid}"

headers = {
    'Accept-Language': 'en',
}


class FSMSystem(BikeShareSystem):

    sync = False

    meta = {
        'system': 'fsm',
        'company': ['FSM Ground Services Ltd.']
    }

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(STATIONS_URL, headers=headers))

        self.stations = list(map(FSMStation, data['stations']))

class FSMStation(BikeShareStation):

    def __init__(self, data):
        super(FSMStation, self).__init__()

        self.name = data['name']
        self.latitude = data['location']['lat']
        self.longitude = data['location']['lng']

        normal_bikes = data['novatechBikes']
        e_bikes = data['omniBikes']

        self.bikes = normal_bikes + e_bikes

        self.extra = {
            'uid': data['id'],
            'number': data['stationNumber'],
            # I think this means if the station works on shabbat
            'shabbat': data['isShabbatStation'],
            'has_ebikes': True,
            'ebikes': e_bikes,
            'normal_bikes': normal_bikes,
        }

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        url = STATION_INFO_URL.format(uid=self.extra['uid'])
        data = json.loads(scraper.request(url, headers=headers))

        e_slots = data['availableOmniPoles']
        normal_slots = data['availableNovatechPoles']

        self.free = e_slots + normal_slots
        self.extra['normal_slots'] = normal_slots
        self.extra['e_slots'] = e_slots

        self.extra['address'] = data['address']
