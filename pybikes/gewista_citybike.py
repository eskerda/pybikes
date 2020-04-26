# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from lxml import etree

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper

__all__ = ['GewistaCityBike']


class GewistaCityBike(BikeShareSystem):

    sync = True

    meta = {
        'system': 'CityBike',
        'company': ['Gewista Werbegesellschaft m.b.H']
    }

    def __init__(self, tag, endpoint, meta):
        super(GewistaCityBike, self).__init__(tag, meta)
        self.endpoint = endpoint

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()
        data = scraper.request(self.endpoint)
        tree = etree.fromstring(data.encode('utf-8'))
        markers = tree.xpath('//station')
        self.stations = list(map(GewistaStation, markers))


class GewistaStation(BikeShareStation):
    def __init__(self, data):
        """
        <station>
            <id>2001</id>
            <internal_id>1046</internal_id>
            <name>Wallensteinplatz</name>
            <boxes>27</boxes>
            <free_boxes>19</free_boxes>
            <free_bikes>8</free_bikes>
            <status>aktiv</status>
            <description/>
            <latitude>48.229912</latitude>
            <longitude>16.371582</longitude>
        </station>
        """
        super(GewistaStation, self).__init__()
        self.name = data.find('name').text
        self.latitude = float(data.find('latitude').text)
        self.longitude = float(data.find('longitude').text)
        self.bikes = int(data.find('free_bikes').text)
        self.free = int(data.find('free_boxes').text)
        self.extra = {
            'uid': data.find('id').text,
            'internal_id': data.find('internal_id').text,
            'status': data.find('status').text,
            'description': data.find('description').text,
            'slots': data.find('boxes').text,
        }
