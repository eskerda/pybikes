# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import HTMLParser

from pyquery import PyQuery as pq

from .base import BikeShareSystem, BikeShareStation
from . import utils
from . import hacks

__all__ = ['Cyclocity','CyclocityStation']

html_parser = HTMLParser.HTMLParser()

class Cyclocity(BikeShareSystem):

    list_url = '/service/carto'
    station_url = '/service/stationdetails/%s/%s'

    sync = False

    meta = {
        'system': 'Cyclocity',
        'company': 'JCDecaux'
    }

    def __init__(self, tag, root_url, city, meta):
        super( Cyclocity, self).__init__(tag, meta)
        self.city = city
        self.root_url = root_url
        self.station_url = self.station_url % (city, '%d')
        self.hacks = []
        
        if tag in hacks.hack_table:
            for hack in hacks.hack_table[self.tag]:
                h = eval('hacks.%s' % hack)()
                self.hacks.append(h)

    def update(self, scraper = utils.PyBikesScraper()):
        url = "{0}{1}".format(self.root_url, self.list_url)
        xml_data = scraper.request(url)
        dom = pq(xml_data.encode('utf-8'), parser = 'xml')
        markers = dom('marker')
        stations = []
        if hasattr(self, 'hacks'):
            for hack in self.hacks:
                markers = hack.markers(markers)

        for index, marker in enumerate(markers):
            station = CyclocityStation(index)
            station.from_xml(marker)
            station.parent = self
            stations.append(station)

        self.stations = stations

class CyclocityStation(BikeShareStation):

    def from_xml(self, xml):

        uid = int(xml.attrib['number'])
        name = xml.attrib['name'].replace('\n','')
        address = xml.attrib['address']
        full_address = xml.attrib['fullAddress']
        is_open = xml.attrib['open']
        bonus = xml.attrib['bonus']
        latitude = float(xml.attrib['lat'])
        longitude = float(xml.attrib['lng'])

        if (name == ""):
            name = "%d - %s" % (uid, address)

        self.name = html_parser.unescape(name)
        self.latitude = latitude
        self.longitude = longitude

        self.extra = {
            'uid': uid,
            'address': html_parser.unescape(address),
            'full_address': html_parser.unescape(full_address),
            'is_open': is_open,
            'bonus': bonus
        }

        return self

    def update(self, scraper = utils.PyBikesScraper()):
        super(CyclocityStation, self).update()
        station_url = self.parent.station_url % self.extra['uid']
        status_xml = scraper.request(self.parent.root_url + station_url)
        status = pq(status_xml.encode('utf-8'), parser = 'xml')
        
        self.bikes = int(status('available').text())
        self.free = int(status('free').text())
        self.extra['total'] = int(status('total').text())
        self.extra['ticket'] = status('ticket').text()
        self.extra['updated'] = status('updated').text()
        self.extra['connected'] = status('connected').text()

        return self