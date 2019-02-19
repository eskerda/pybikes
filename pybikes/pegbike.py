# -*- coding: utf-8 -*-
# Copyright (C) 2019, mmmaia <mauricio.maia@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper

class PegBike(BikeShareSystem):
    sync = True
    meta = {
        'system': 'PegBike',
        'company': ['PegBike']
    }

    def __init__(self, tag, meta, url):
        super(PegBike, self).__init__(tag, meta)
        self.feed_url = url

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()

        body = json.dumps({"tipo": "getstations"})
        json_data = scraper.request(
                self.feed_url,
                method='POST',
                data=body,
                headers={"Content-Type": "application/json"}
        )

        station_data = json.loads(json_data)
        stations = []
        for data in station_data:
            station = BikeShareStation()
            station.name = data['nome']
            station.latitude = float(data['latitude'])
            station.longitude = float(data['longitude'])
            station.bikes = int(data['bikes'])
            station.free = int(data['vagas'])
            station.extra = {
                'address': data['endereco'],
                'uid': int(data['id']),
                'online': data['status'] == u'Em operação'
            }
            stations.append(station)
        self.stations = stations
