# -*- coding: utf-8 -*-
# Copyright (C) 2019, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class BicincittaMixin(object):
    stations_url = 'http://www.bicincitta.com/frmLeStazioniComune.aspx/RefreshStations'  # NOQA
    stations_status_url = 'http://www.mimuovoinbici.it/frmLeStazioni.aspx/RefreshPopup'  # NOQA

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    @staticmethod
    def get_stations(city_id, scraper):
        payload = json.dumps({'IDComune': str(city_id)})
        response = scraper.request(BicincittaMixin.stations_url, data=payload,
                                   headers=BicincittaMixin.headers,
                                   method='POST')
        return json.loads(response)

    @staticmethod
    def get_station_status(station_id, scraper):
        payload = json.dumps({'IDStazione': str(station_id)})
        response = scraper.request(BicincittaMixin.stations_status_url,
                                   data=payload,
                                   headers=BicincittaMixin.headers,
                                   method='POST')
        return json.loads(response)


class Bicincitta(BikeShareSystem, BicincittaMixin):
    sync = False

    source_url = 'http://www.bicincitta.com/frmLeStazioni.aspx?ID={city_id}'

    meta = {
        'system': 'Bicincittà',
        'company': ['Comunicare S.r.l.']
    }

    def __init__(self, tag, meta, city_ids):
        super(Bicincitta, self).__init__(tag, meta)
        self.meta['source'] = self.source_url.format(city_id=city_ids[0])
        self.city_ids = city_ids

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        self.stations = [s for s in self.parse_stations(scraper)]

    def parse_stations(self, scraper):
        for city in self.city_ids:
            data = self.get_stations(city, scraper)
            for s in data['d'][1:]:
                params = s.split(u'§')
                yield BicincittaStation(*params)


class BicincittaStation(BikeShareStation, BicincittaMixin):

    station_statuses = {
        0: 'online',
        1: 'maintenance',
        2: 'offline',
        3: 'under construction',
        4: 'planned',
    }

    def __init__(self, uid, lat, lng, name, number, status):
        super(BicincittaStation, self).__init__()

        self.name = name
        self.latitude = float(lat)
        self.longitude = float(lng)
        self.extra = {
            'uid': uid,
            'number': int(number),
            'status': self.station_statuses[int(status)],
        }

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = self.get_station_status(self.extra['uid'], scraper)
        _, reviews, score, _, status, _, _ = data['d'].split(u'§')

        self.bikes = status.count('4')
        self.free = status.count('0')
        self.extra['score'] = float(score.replace(',', '.'))
        self.extra['reviews'] = int(reviews)
