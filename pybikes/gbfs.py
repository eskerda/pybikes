# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
try:
    # Python 2
    from urlparse import urljoin
except ImportError:
    # Python 3
    from urllib.parse import urljoin

from pybikes import BikeShareSystem, BikeShareStation, exceptions
from pybikes.utils import PyBikesScraper

try:
    # Python 2
    unicode
except NameError:
    # Python 3
    unicode = str


class Gbfs(BikeShareSystem):

    station_cls = None

    def __init__(self, tag, meta, feed_url, force_https=False):
        # Add feed_url to meta in order to be exposed to the API
        meta['gbfs_href'] = feed_url
        super(Gbfs, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.force_https = force_https

    @property
    def default_feeds(self):
        url = self.feed_url
        return {
            "station_information": urljoin(url, 'station_information.json'),
            "station_status": urljoin(url, 'station_status.json'),
        }

    def get_feeds(self, url, scraper, force_https):
        feed_data = scraper.request(url, raw=True)
        if scraper.last_request.status_code >= 400:
            # GBFS service description not found. Try to guess based on
            # defaults
            return self.default_feeds

        feed_data = json.loads(feed_data)
        feeds = {}

        # Prefer "en", if not, take any
        lang = "en"

        if lang in feed_data['data']:
            feeds = feed_data['data'][lang]
        else:
            feeds = list(feed_data['data'].values()).pop()

        if isinstance(feeds, dict):
            feeds = feeds['feeds']

        for feed in feeds:
            if force_https:
                # Feed published with the wrong protocol
                feed['url'] = feed['url'].replace('http://', 'https://')

        return {feed['name']: feed['url'] for feed in feeds}


    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        feeds = self.get_feeds(self.feed_url, scraper, self.force_https)

        # Station Information and Station Status data retrieval
        station_information = json.loads(
            scraper.request(feeds['station_information'])
        )['data']['stations']
        station_status = json.loads(
            scraper.request(feeds['station_status'])
        )['data']['stations']
        # Aggregate status and information by uid
        # Note there's no guarantee that station_status has the same
        # station_ids as station_information.
        station_information = {s['station_id']: s for s in station_information}
        station_status = {s['station_id']: s for s in station_status}
        # Any station not in station_information will be ignored
        stations = [
            (station_information[uid], station_status[uid])
            for uid in station_information.keys()
        ]
        self.stations = []
        for info, status in stations:
            info.update(status)
            try:
                station = self.station_cls(info)
            except exceptions.StationPlannedException:
                continue
            self.stations.append(station)


class GbfsStation(BikeShareStation):

    def __init__(self, info):
        """
        Example info variable:
        {u'is_installed': 1, u'post_code': u'null', u'capacity': 31,
        u'name': u'Ft. York / Capreol Crt.', u'cross_street': u'null',
        u'num_bikes_disabled': 0, u'last_reported': 1473969337,
        u'lon': -79.395954, u'station_id': u'7000', u'is_renting': 1,
        u'num_docks_available': 26, u'num_docks_disabled': 0,
        u'address': u'Ft. York / Capreol Crt.', u'lat': 43.639832,
        u'num_bikes_available': 5, u'is_returning': 1}

        So let's extract the dataaa
        """
        super(GbfsStation, self).__init__()
        if not info['is_installed']:
            raise exceptions.StationPlannedException()

        self.name = unicode(info['name'])
        self.bikes = int(info['num_bikes_available'])
        self.free = int(info['num_docks_available'])
        self.latitude = float(info['lat'])
        self.longitude = float(info['lon'])
        self.extra = {
            'uid': info['station_id'],
            'renting': info['is_renting'],
            'returning': info['is_returning'],
            'last_updated': info['last_reported'],
        }

        if 'address' in info:
            self.extra['address'] = info['address']

        if 'num_ebikes_available' in info:
            self.extra['has_ebikes'] = True
            self.extra['ebikes'] = int(info['num_ebikes_available'])

        if 'rental_methods' in info:
            payment = list(map(unicode.lower, info['rental_methods']))
            self.extra['payment'] = payment
            self.extra['payment-terminal'] = 'creditcard' in payment


Gbfs.station_cls = GbfsStation
