# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from pyquery import PyQuery as pq

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['GewistaCityBike']

class GewistaCityBike(BikeShareSystem):

    sync = True

    meta = {
        'system': 'CityBike',
        'company': 'Gewista Werbegesellschaft m.b.H'
    }

    def __init__(self, tag, endpoint, meta):
        super(GewistaCityBike, self).__init__(tag, meta)
        self.endpoint = endpoint

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        data = scraper.request(self.endpoint)
        dom  = pq(data.encode('utf-8'), parser = 'xml')
        markers = dom('station')
        stations = []
        for index, marker in enumerate(markers):
            station = GewistaStation(index)
            station.from_xml(marker)
            stations.append(station)
        self.stations = stations

class GewistaStation(BikeShareStation):
    def from_xml(self, xml_data):
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
        xml_data = pq(xml_data, parser='xml')

        self.name      = xml_data('name').text()
        self.latitude  = float(xml_data('latitude').text())
        self.longitude = float(xml_data('longitude').text())
        self.bikes     = int(xml_data('free_bikes').text())
        self.free      = int(xml_data('free_boxes').text())

        self.extra = {
            'uid': int(xml_data('id').text()),
            'internal_id': int(xml_data('internal_id').text()),
            'status': xml_data('status').text(),
            'description': xml_data('description').text(),
            'slots': int(xml_data('boxes').text())
        }

