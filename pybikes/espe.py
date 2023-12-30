# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json
import time
from base64 import b64encode, b64decode
# Python 2
from builtins import bytes, str

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

STATIONS_URL = '{endpoint}/station/stationPublic?idEmpresa={uid}'


class Espe(BikeShareSystem):

    @property
    def auth_headers(self):
        fixed = str(b64decode('QklDSVMtQklYMjAyM0RFU19Vc2VyOkJJQ0lTLUJJWDIwMjNERVNfUGFzc3dvcmQ6'), 'utf-8')
        timestamp = str(int(time.time()) * 1000)
        token = b64encode(bytes(fixed + timestamp, 'utf-8'))

        return {
            'Authorization': 'Basic ' + str(token, 'utf-8')
        }

    def __init__(self, tag, meta, uid, endpoint):
        super(Espe, self).__init__(tag, meta)
        self.endpoint = endpoint
        self.uid = uid

    @property
    def stations_url(self):
        return STATIONS_URL.format(endpoint=self.endpoint, uid=self.uid)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.stations_url,
                                          headers=self.auth_headers,
                                          method='GET'))
        # There is a lot of trash on the feed, 'PUBLICA' means it is displayed
        # on their map
        public_stations = filter(lambda s: s['tipoEstacion'] == 'PUBLICA',
                                 data['data']['estacionesList'])

        self.stations = list(map(EspeStation, public_stations))

class EspeStation(BikeShareStation):
    def __init__(self, data):
        super(EspeStation, self).__init__()

        self.name = data['nombreEstacion']
        self.latitude = float(data['latitud'])
        self.longitude = float(data['longitud'])

        self.bikes = int(data['bicicletasEnEstacion'])
        self.free = int(data['bahiasLibres'])

        self.extra = {
            'uid': data['idEstaciones'],
            'address': data['direccion'],
            'slots': data['bahiasEnTotal'],
            # [A]ctivo, [I]nactivo
            'online': data['estado'] == 'A',
        }
