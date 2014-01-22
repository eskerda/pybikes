# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from .base import BikeShareSystem, BikeShareStation
from . import utils

from lxml import etree

__all__ = ['Keolis_v2', 'KeolisStation_v2']

xml_parser = etree.XMLParser(recover = True)

class Keolis_v2(BikeShareSystem):

    sync = False

    meta = {
        'system': 'Keolis',
        'company': 'Keolis'
    }

    _list_url = '/stations/xml-stations.aspx'
    _station_url = '/stations/xml-station.aspx?borne={id}'

    def __init__(self, tag, feed_url, meta):
        super(Keolis_v2, self).__init__(tag, meta)
        self.feed_url = feed_url + self._list_url
        self.station_url = feed_url + self._station_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        raw_list = scraper.request(self.feed_url).encode('utf-16')
        xml_list = etree.fromstring(raw_list, xml_parser)

        stations = []
        for index, marker in enumerate(xml_list.iter('marker')):
            station = KeolisStation_v2(index, marker, self.station_url)
            stations.append(station)
        self.stations = stations

class KeolisStation_v2(BikeShareStation):
    def __init__(self, index, marker, station_url):
        super(KeolisStation_v2, self).__init__(index)

        self.name      = marker.get('name')
        self.latitude  = float(marker.get('lat'))
        self.longitude = float(marker.get('lng'))
        self.extra     = {
            'uid': int(marker.get('id'))
        }

        self._station_url = station_url.format(id = self.extra['uid'])

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        raw_status = scraper.request(self._station_url).encode('utf-16')
        xml_status = etree.fromstring(raw_status, xml_parser)
        self.bikes = int(xml_status.find('bikes').text)
        self.free  = int(xml_status.find('attachs').text)

        self.extra['address'] = xml_status.find('adress').text.title()

        # TODO: Try to standarize these fields
        # 0 means online, 1 means temporarily unavailable
        # are there more status?
        self.extra['status'] = xml_status.find('status').text

        # payment: AVEC_TPE | SANS_TPE
        # as in, accepts bank cards or not
        self.extra['payment'] = xml_status.find('paiement').text

        # Update time as in 47 seconds ago: '47 secondes'
        self.extra['lastupd'] = xml_status.find('lastupd').text

