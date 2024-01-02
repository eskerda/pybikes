# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded

STATIONS_URL = '{endpoint}/cxf/am/station/map/search'
FILES_URL = '{endpoint}/cxf/fm/files/{file_id}'


def file_url(endpoint, file_id):
    return FILES_URL.format(endpoint=endpoint, file_id=file_id)


class WeGoShare(Bounded, BikeShareSystem):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    meta = {
        "company": ['Wegoshare, Lda'],
    }

    def __init__(self, tag, meta, endpoint, bbox=None):
        meta['company'] += WeGoShare.meta['company']
        super(WeGoShare, self).__init__(tag, meta, bounds=bbox)
        self.endpoint = endpoint

    @property
    def stations_url(self):
        return STATIONS_URL.format(endpoint=self.endpoint)

    def update(self, scraper=None):
        payload = json.dumps({'isPublic': True, 'limit': -1})
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.stations_url,
                                          data=payload,
                                          headers=WeGoShare.headers,
                                          method='POST'))
        stations = []
        for station_data in data['results']:
            # discard planned stations
            if station_data['stationStatus'] == 'PLANNED':
                continue
            station = WeGoShareStation(station_data, self.endpoint)
            stations.append(station)

        self.stations = stations


class WeGoShareStation(BikeShareStation):
    def __init__(self, data, endpoint):
        super(WeGoShareStation, self).__init__()
        self.endpoint = endpoint

        self.name = data['name']
        self.latitude = float(data['areaCentroid']['latitude'])
        self.longitude = float(data['areaCentroid']['longitude'])

        # totalLocked: primaryLocked (station) + secondaryLocked (overflow)
        # overflow means locking the bike near the station when it is full
        self.bikes = int(data['totalLockedCycleCount'])
        self.free = int(data['freeDocksCount'])

        self.extra = {
            'uid': data['id'],
            'description': data['description'],
            'address': data['address'],
            'online': data['stationStatus'] == 'OPEN',
            'last_update': data['lastUpdateCycleCountAt'],
            'photo': file_url(endpoint, data['photoId']) if 'photoId' in data else None,
        }
