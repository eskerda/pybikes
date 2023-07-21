# -*- coding: utf-8 -*-
# Copyright (C) 2010-2023, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

class WeeloAPI:

    endpoint = 'https://api.weelo.it'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def authorization(self):
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }

    def request(self, scraper, * args, ** kwargs):
        scraper.headers.update({
            'user-agent': 'okhttp/4.9.1',
        })
        resp = scraper.request(* args, ** kwargs)

        if scraper.last_request.status_code == 401:
            # do auth
            auth = json.loads(self.authorize(scraper))
            assert 'access_token' in auth, 'Authorization error'
            scraper.headers.update({
                'authorization': 'Bearer %s' % auth['access_token'],
            })
            return self.request(scraper, * args, ** kwargs)

        return resp


    def authorize(self, scraper):
        return self.request(scraper, self.endpoint + '/connect/token', method='POST', data=self.authorization)

    def stations(self, city_id, scraper):
        data = self.request(scraper, self.endpoint + '/resources/stations', method='GET', params={'idCity': city_id, 'serviceType': 1})
        return json.loads(data)

    def systems(self, scraper):
        data = self.request(scraper, self.endpoint + '/resources/services', method='GET')
        return json.loads(data)


class Weelo(BikeShareSystem):

    authed = True

    meta = {
        'system': 'Weelo',
        'company': ['Bicincitta Italia S.r.l.'],
    }

    def __init__(self, tag, meta, city_ids, key):
        super(Weelo, self).__init__(tag, meta)
        self.city_ids = city_ids
        self.key = key

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        client = WeeloAPI(** self.key)
        stations = []
        for city_id in self.city_ids:
            stations += list(map(WeeloStation, client.stations(city_id, scraper)))
        self.stations = stations

class WeeloStation(BikeShareStation):
    def __init__(self, info):
        super(WeeloStation, self).__init__()

        self.name = info['name']
        self.latitude = info['latitude']
        self.longitude = info['longitude']

        # lol
        normal_bikes = info['countMuscularBikesAvailable']
        e_bikes = info['countAssistedBikesAvailable']
        self.bikes = normal_bikes + e_bikes
        self.free = info['countFreePlacesAvailable']

        self.extra = {
            'uid': info['idStation'],
            'address': info['address'],
            'has_ebikes': 'countAssistedBikesAvailable' in info,
            'ebikes': e_bikes,
            'normal_bikes': normal_bikes,
            'status': info['state'],
            'slots': info['totalPlaces'],
        }
