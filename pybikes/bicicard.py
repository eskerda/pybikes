# -*- coding: utf-8 -*-
# Copyright (C) 2023, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.contrib import TSTCache

AUTH_URL = '{endpoint}/api/certificado'
STATIONS_URL = '{endpoint}/apiapp/SBancada/Estado/TodosSimple'

cache = TSTCache(delta=3600)


def stupidict(thing):
    """ makes all keys on a dict lowercase. Useful when different endpoints
        serve the same shit but sometimes its camelCase and sometimes its
        CamelCase
    """
    if isinstance(thing, list):
        return [stupidict(t) for t in thing]
    elif isinstance(thing, dict):
        return dict((k.lower(), stupidict(v)) for k, v in thing.items())
    else:
        return thing


class Bicicard(BikeShareSystem):

    meta = {
        'system': 'bicicard',
        'company': ['Instituto Tecnológico de Castilla y León (ITCL)'],
    }

    def __init__(self, tag, meta, endpoint):
        super(Bicicard, self).__init__(tag, meta)
        self.endpoint = endpoint

    @property
    def auth_url(self):
        return AUTH_URL.format(endpoint=self.endpoint)

    @property
    def stations_url(self):
        return STATIONS_URL.format(endpoint=self.endpoint)

    def update(self, scraper=None):
        headers = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; ROCINANTE FIRE Build/9001',
            'DeviceModel': 'ROCINANTE FIRE',
        }
        scraper = scraper or PyBikesScraper(cache)
        cert = json.loads(scraper.request(self.auth_url, headers=headers))
        cert = stupidict(cert)
        headers.update({
            'Thumbprint': cert['thumbprint'],
        })
        data = scraper.request(self.stations_url, headers=headers, skip_cache=True)
        info = map(stupidict, json.loads(data))
        self.stations = list(map(BicicardStation, info))


class BicicardStation(BikeShareStation):
    def __init__(self, data):
        super(BicicardStation, self).__init__()

        self.name = data['nombre']
        self.latitude = data['latitud']
        self.longitude = data['longitud']

        bikes = data['numerobicicletasnormales']
        ebikes = data['numerobicicletaselectricas']
        self.bikes = bikes + ebikes
        self.free = data['numerocandadoslibres']

        self.extra = {
            'uid': data['id'],
            'normal_bikes': bikes,
            'ebikes': ebikes,
            'slots': data['numerocandados'],
            'online': data['ispuestoonline'],
        }
