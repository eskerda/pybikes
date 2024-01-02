# -*- coding: utf-8 -*-
# Copyright (C) 2015, bparmentier <dev@brunoparmentier.be>
# Copyright (C) 2016, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Copyright (C) 2016, eskerda <eskerda@gmail.com>
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper, Bounded


class BaseSystem(BikeShareSystem):
    meta = {"system": "EasyBike", "company": ["Brainbox Technology", "Smoove SAS"]}


class EasyBike(Bounded, BaseSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'EasyBike',
        'company': ['Brainbox Technology', 'Smoove SAS']
    }

    feed_url = 'http://reseller.easybike.gr/{city_uid}/api.php'

    def __init__(self, tag, meta, city_uid, bbox=None):
        super(EasyBike, self).__init__(tag, meta, bounds=bbox)
        self.feed_url = EasyBike.feed_url.format(city_uid=city_uid)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        stations = self.get_stations(data)
        self.stations = list(stations)

    def get_stations(self, data):
        for station in data['stations']:
            name = station['description']
            longitude = float(station['lng'])
            latitude = float(station['lat'])
            bikes = int(station['free_bikes'])
            free = int(station['free_spaces'])
            extra = {
                'slots': int(station['total_spaces'])
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            yield station


class EasyBikeNew(BaseSystem):
    sync = True
    FEED_URL = "https://{city_uid}.easybike.gr:8001/imet/v2/availability"

    def __init__(self, tag, meta, city_uid):
        super(EasyBikeNew, self).__init__(tag, meta)
        self.city_uid = city_uid

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        data = json.loads(
            scraper.request(
                self.FEED_URL.format(city_uid=self.city_uid),
                headers={
                    "Authorization": "Basic aW1ldDIwMTkwNTAxOkomZ2UjdXBQbUBNbT81aGI0eTZZ",
                },
            )
        )

        stations = data["stations"]

        self.stations = []
        for data in stations:
            station = BikeShareStation()
            station.name = data["label"]
            station.latitude = float(data["lat"])
            station.longitude = float(data["lng"])
            station.bikes = int(data["available"])
            station.free = int(data["spaces"])
            station.extra = {
                "uid": data["station_id"],
            }
            self.stations.append(station)
