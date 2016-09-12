# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__=['Gbfs', 'GbfsStation']

class Gbfs(BikeShareSystem):

    def __init__(self, tag, meta, feed_url):
        super(Gbfs, self).__init__(tag, meta)
        self.feed_url=feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper=utils.PyBikesScraper()

        # Make the request to gbfs.json and convert to json
        html_data=json.loads(scraper.request(self.feed_url, raw=True))

        # Create a dict with name-url pairs for easier access
        # of urls (just in case)

        feeds={}
        for feed in html_data['data']['en']['feeds']:
            feeds[feed['name']]=feed['url']

        '''Station Information and Station Status data retrieval
        '''
        station_information=json.loads(scraper.request(feeds['station_information']))
        station_status=json.loads(scraper.request(feeds['station_status']))

        for info, status in zip(station_information['data']['stations'],\
        station_status['data']['stations']):
            self.stations.append(GbfsStation(info, status))


class GbfsStation(BikeShareStation):

    def __init__(self, info, status):
        """
        Example info variable:
        {u'post_code': u'null', u'capacity': 31, u'name': u'Ft. York / Capreol Crt.',
        u'cross_street': u'null', u'lon': -79.395954, u'station_id': u'7000', u'address':
        u'Ft. York / Capreol Crt.', u'lat': 43.639832}

        Example status variable:
        {u'last_reported': 1473627463, u'num_bikes_disabled': 3, u'num_docks_available': 16,
        u'is_renting': 1, u'station_id': u'7000', u'num_docks_disabled': 0, u'is_installed':
        1, u'num_bikes_available': 12, u'is_returning': 1}

        So let's extract the dataaa

        Note: Maybe it's valuable to check every time the station_ids to see if
        they match.
        """
        super(GbfsStation, self).__init__()

        self.station_id=[info['station_id'] if
                info['station_id']==status['station_id'] else 'Wrong']
        self.name=str(info.get('name'))
        self.status=['Active' if status['is_renting'] and
            status['is_installed'] else 'Inactive']
        self.bikes=status.get('num_bikes_available')
        self.free=status.get('num_docks_available')
        self.latitude=float(info.get('lat'))
        self.longitude=float(info.get('lon'))
