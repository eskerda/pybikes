# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class BySykkel(BikeShareSystem):

    authed = True

    meta = {
        'system': 'BySykkel',
        'company': ['Urban Infrastructure Partner']
    }

    def __init__(self, tag, meta, feed_url, feed_details_url, key):
        super(BySykkel, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.feed_details_url = feed_details_url
        self.key = key

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        scraper.headers['Client-Identifier'] = self.key

        self.stations = []


        stations_data = json.loads(scraper.request(self.feed_url))
        details_data = json.loads(scraper.request(self.feed_details_url))

        # Aggregate status and information by uid
        stations_data = {s['id']: s for s in stations_data['stations']}
        details_data = {s['id']: s for s in details_data['stations']}

        # Join stationsdata in stations
        stations = [
            (stations_data[id], details_data[id])
            for id in stations_data.keys()
        ]

        # append all data to info part of stations and create objects of this
        for info, status in stations:
            info.update(status)

            station = BySykkelStation(info)

            self.stations.append(station)



class BySykkelStation(BikeShareStation):
    def __init__(self, info):

        super(BySykkelStation, self).__init__()

        self.name = info['title']

        self.longitude = float(info['center']['longitude'])
        self.latitude  = float(info['center']['latitude'])

        self.bikes = info['availability']['bikes']
        self.free = info['availability']['locks']
        self.extra = {
            'uid': info['id'],
            'placement': info['subtitle'],
        }
