# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from .utils import PyBikesScraper

# Documented at
# http://dev.opentripplanner.org/apidoc/0.15.0/ns0_bikeRentalStationList.html


class OTP(BikeShareSystem):
    # Please note company is not provided by this class and should be added on
    # the metadata JSON, as OTP implementation is generic for different systems
    meta = {
        'system': 'OTP',
    }

    authed = True

    def __init__(self, tag, feed_url, meta, key):
        super(OTP, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.key = key

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        scraper.headers['Accept'] = 'application/json'
        scraper.headers['digitransit-subscription-key'] = self.key

        data = json.loads(scraper.request(self.feed_url))
        stations = []
        for st in data['stations']:
            name = st['name']
            bikes = st['bikesAvailable']
            free = st['spacesAvailable']
            lat = st['y']
            lng = st['x']
            extra = {
                'uid': st['id']
            }
            station = BikeShareStation(name, lat, lng, bikes, free, extra)
            stations.append(station)

        self.stations = stations
