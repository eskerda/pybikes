# -*- coding: utf-8 -*-
# Copyright (C) 2019, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import json

try:
    # Python 2
    from urlparse import urljoin
except ImportError:
    # Python 3
    from urllib.parse import urljoin

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class BicincittaMixin(object):
    stations_url = 'https://www.bicincitta.com/frmLeStazioniComune.aspx/RefreshStations'  # NOQA
    stations_status_url = 'https://www.bicincitta.com/frmLeStazioni.aspx/RefreshPopup'  # NOQA

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
    endpoint = 'https://www.bicincitta.com/'
    source_url = 'frmLeStazioni.aspx?ID={city_id}'

    meta = {
        'system': 'Bicincittà',
        'company': ['Comunicare S.r.l.']
    }

    def __init__(self, tag, meta, city_ids, endpoint=None):
        super(Bicincitta, self).__init__(tag, meta)
        self.city_ids = city_ids
        self.endpoint = endpoint or self.endpoint
        source_url = self.source_url.format(city_id=city_ids[0])
        self.meta['source'] = urljoin(self.endpoint, source_url)

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

    def __init__(self, uid, lat, lng, name, number, status, *_):
        # More shit might come from this ingnominious string, personally I do
        # care at this point what other information can be found in this, so
        # to avoid making it fail we just ignore anything else
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
        # More shit might come from this ingnominious string, personally I do
        # care at this point what other information can be found in this, so
        # to avoid making it fail we just limit it to the first 5 fields.
        _, reviews, score, _, status = data['d'].split(u'§')[:5]

        self.bikes = status.count('4')
        self.free = status.count('0')
        self.extra['score'] = float(score.replace(',', '.'))
        self.extra['reviews'] = int(reviews)
