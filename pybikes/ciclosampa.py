# -*- coding: utf-8 -*-
# Copyright (C) 2014, iomartin <iomartin@iomartin.net>
# Distributed under the LGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


USERAGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36"  # NOQA


class CicloSampa(BikeShareSystem):
    sync = True
    meta = {
        'system': 'CicloSampa',
        'company': ['Bradesco Seguros']
    }

    def __init__(self, tag, meta, url):
        super(CicloSampa, self).__init__(tag, meta)
        self.feed_url = url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(USERAGENT)

        body = json.dumps({"tipo": "getstations"})
        json_data = scraper.request(
                self.feed_url,
                method='POST',
                data=body,
                headers={"Content-Type": "application/json"})
        stations = json.loads(json_data)

        self.stations = []

        for station in stations:
            self.stations.append(CicloSampaStation(station))


class CicloSampaStation(BikeShareStation):
    def __init__(self, data):
        super(CicloSampaStation, self).__init__()
        self.name = data['nome']
        self.latitude = float(data['latitude'])
        self.longitude = float(data['longitude'])
        self.bikes = int(data['bikes'])
        self.free = int(data['vagas'])
        self.extra = {
            'address': data['endereco'],
            'uid': int(data['id']),
            'slots': int(data['bikes']) + int(data['bikes'])
        }
