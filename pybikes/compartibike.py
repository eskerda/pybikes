# -*- coding: utf-8 -*-
# Copyright (C) 2016, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Copyright (C) 2016, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes import utils


class CompartiBike(BikeShareSystem):

    # Please note company is not provided by this class and should be
    # added on the metadata JSON, as CompartiBike implementation is
    # generic for different systems
    meta = {
        'system': 'CompartiBike'
    }

    def __init__(self, tag, meta, feed_url, bounding_box=None):
        super(CompartiBike, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.bounding_box = bounding_box

    def update(self, scraper=None):
        scraper = scraper or utils.PyBikesScraper()
        scraper.ssl_verification = False

        stations = []

        data = json.loads(scraper.request(self.feed_url))
        for station in data:
            # Skip "Loldesign" stations
            if station['googleMapY'] == "" or station['googleMapX'] == "":
                continue

            longitude = float(station['googleMapY'])
            latitude = float(station['googleMapX'])

            name = station['name']
            free = int(station['available_slots_size'])
            bikes = int(station['unavailable_slots_size'])

            extra = {
                'uid': int(station['id']),
                'open': station['status'] == 'Ativa',
                'number': int(station['station_number']),
                'bike_uids': [bike['id'] for bike in station['bikes']]

            }

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)

        if self.bounding_box:
            stations = utils.filter_bounds(stations, None, self.bounding_box)

        self.stations = list(stations)
