# -*- coding: utf-8 -*-
# Copyright (C) 2016, Ben Caller <bcaller@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import json
import hashlib

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Bonopark', 'BonoparkStation']

SECRET = 'APP_INICIO'
BODY_DICT = {
    'dni': SECRET,
    'id_auth': SECRET,
    'id_security': hashlib.md5(SECRET * 2).hexdigest() + hashlib.md5(SECRET).hexdigest()
}

COLORS = ['green', 'red', 'yellow', 'gray']

class Bonopark(BikeShareSystem):
    sync = True
    meta = {
        'system': 'Bonopark',
        'company': 'Bonopark'
    }

    def __init__(self, tag, meta, url):
        super(Bonopark, self).__init__(tag, meta)
        self.feed_url = url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent("Apache-HttpClient/UNAVAILABLE (java 1.4)")
        scraper.headers['Content-Type'] = 'application/json'
        data = json.loads(scraper.request(self.feed_url, 'POST', data=json.dumps(BODY_DICT)))
        self.stations = map(BonoparkStation, data['estaciones'])


class BonoparkStation(BikeShareStation):
    def __init__(self, data):
        super(BonoparkStation, self).__init__()
        self.name = data['nombre']
        self.latitude = float(data['latitud'])
        self.longitude = float(data['longitud'])
        self.bikes = int(data['bicis_enganchadas'])
        self.free = int(data['bases_libres'])
        self.extra = {
            'station_id': data['numero_estacion'],
            'uid': int(data['idestacion']),
            'address': data['direccion'],
            'online': data['activo'] == "1" and data['no_disponible'] == "0",
            'slots': int(data['numero_bases']),
            'light': COLORS[int(data['luz'])]
        }
