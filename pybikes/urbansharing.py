# -*- coding: utf-8 -*-
# Distributed under the LGPL license, see LICENSE.txt
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

FEED_URL = 'https://core.urbansharing.com/public/api/v1/graphql?operationName=DockGroups&variables=%7B%22systemId%22%3A%22{tag}%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%226afd0a33ab1a81d87dd31830e4e3f3da6f9e0881a9a07427b59bf1dec6fd692e%22%7D%7D'


class UrbanSharing(BikeShareSystem):
    def __init__(self, tag, meta):
        super(UrbanSharing, self).__init__(tag, meta)

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()

        feed_url = FEED_URL.format(tag=self.tag)
        stations_data = json.loads(scraper.request(feed_url))

        stations = []

        for station_data in stations_data['data']['dockGroups']:
            station = UrbanSharingStation(station_data)
            stations.append(station)

        self.stations = stations


class UrbanSharingStation(BikeShareStation):
    def __init__(self, data):
        super(UrbanSharingStation, self).__init__()

        self.latitude = float(data['coord']['lat'])
        self.longitude = float(data['coord']['lng'])
        self.name = data['title']
        self.bikes = int(data['availabilityInfo']['availableVehicles'])
        self.free = int(data['availabilityInfo']['availableDocks'])
        self.extra = {
            'uid': data['id'],
            'address': data['subTitle'],
            'online': data['state'] == 'active'
        }
