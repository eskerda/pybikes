# -*- coding: utf-8 -*-
# Copyright (C) 2019, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import re
import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.compat import urljoin



class BicincittaMixin(object):
    stations_path = 'frmLeStazioniComune.aspx/RefreshStations'
    stations_status_path = 'frmLeStazioni.aspx/RefreshPopup'

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    @staticmethod
    def get_stations(city_id, endpoint, scraper):
        payload = json.dumps({'IDComune': str(city_id)})
        url = urljoin(endpoint, BicincittaMixin.stations_path)
        response = scraper.request(url, data=payload,
                                   headers=BicincittaMixin.headers,
                                   method='POST')
        return json.loads(response)

    @staticmethod
    def get_station_status(station_id, endpoint, scraper):
        payload = json.dumps({'IDStazione': str(station_id)})
        url = urljoin(endpoint, BicincittaMixin.stations_status_path)
        response = scraper.request(url,
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
            data = self.get_stations(city, self.endpoint, scraper)
            for s in data['d'][1:]:
                params = s.split(u'§')
                yield BicincittaStation(self.endpoint, *params)


class BicincittaStation(BikeShareStation, BicincittaMixin):

    station_statuses = {
        0: 'online',
        1: 'maintenance',
        2: 'offline',
        3: 'under construction',
        4: 'planned',
    }

    def __init__(self, endpoint, uid, lat, lng, name, number, status, *_):
        # More shit might come from this ingnominious string, personally I do
        # care at this point what other information can be found in this, so
        # to avoid making it fail we just ignore anything else
        super(BicincittaStation, self).__init__()
        self.endpoint = endpoint
        self.name = name
        self.latitude = BicincittaStation.parse_shitty_float(lat)
        self.longitude = BicincittaStation.parse_shitty_float(lng)
        self.extra = {
            'uid': uid,
            'number': int(number),
            'status': self.station_statuses[int(status)],
        }

    @staticmethod
    def parse_shitty_float(blergh):
        # One particular station info on 'bici-perugia' has the following
        # 1647§43.10652759999998612.38971570000001§12.38971570000001§08. Bellucci§8§3§0
        # which means we need to know how to parse
        # 43.10652759999998612.38971570000001 as just
        # 43.106527599999986
        try:
            return float(re.search(r'\d+\.\d{5,15}', blergh).group())
        # Worst case, do what we were doing and fail
        except:
            return float(blergh)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = self.get_station_status(self.extra['uid'], self.endpoint, scraper)
        # More shit might come from this ingnominious string, personally I do
        # care at this point what other information can be found in this, so
        # to avoid making it fail we just limit it to the first 5 fields.
        _, reviews, score, _, status = data['d'].split(u'§')[:5]

        self.bikes = status.count('4')
        self.free = status.count('0')
        self.extra['score'] = float(score.replace(',', '.'))
        self.extra['reviews'] = int(reviews)
