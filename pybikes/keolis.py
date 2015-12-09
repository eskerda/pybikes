# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

from lxml import etree
import lxml.html

from .base import BikeShareSystem, BikeShareStation
from . import utils


__all__ = ['Keolis', 'KeolisStation', 'Keolis_v2', 'KeolisStation_v2']

xml_parser = etree.XMLParser(recover = True)
_re_float = "([+-]?\\d*\\.\\d+)(?![-+0-9\\.])"

class Keolis(BikeShareSystem):
    sync = True

    meta = {
        'system': 'Keolis',
        'company': 'Keolis'
    }

    _re_fuzzle = '\"latitude\"\:\ \"{0}\"\,\ '\
                 '\"longitude\"\:\ \"{0}\"\,\ '\
                 '\"text\"\:\ \"(.*?)\"\,\ '\
                 '\"markername'.format(_re_float)
    _re_num_name = "\#(\d+)\ \-\ (.*)" # #10 - Place Lyautey

    def __init__(self, tag, meta, feed_url):
        super(Keolis, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        raw_fuzzle = scraper.request(self.feed_url)
        data = re.findall(Keolis._re_fuzzle, raw_fuzzle)
        self.stations = map(KeolisStation, data)

class KeolisStation(BikeShareStation):
    def __init__(self, data):
        """
        fuzzle is something like
        Must be utf8 encoded and string-escaped
        <div class="gmap-popup">
            <div class="gmap-infobulle">
                <div class="gmap-titre">#16 - Universite Sud</div>
                <div class="gmap-adresse">
                    AVENUE DE L'UNIVERSITE FACE A L'ENTREE DE L'UNIVERSITE
                </div>
                <div class="gmap-velos">
                    <table>
                        <tr>
                            <td class="ok">
                                <strong>9</strong> vélos disponibles
                            </td>
                            <td class="ok">
                                <strong>17</strong> places disponibles
                            </td>
                            <td>
                                <acronym title="Carte Bancaire">CB</acronym>
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="gmap-datemaj">
                    dernière mise à jour il y a <strong>00 min</strong>
                </div>
            </div>
        </div>
        """
        super(KeolisStation, self).__init__()
        fuzzle = lxml.html.fromstring(
            data[2].encode('utf8').decode('string-escape')
        )
        num_name = re.findall(
            Keolis._re_num_name,
            fuzzle.xpath('//div[@class="gmap-titre"]/text()')[0]
        )[0]

        bikes_places_upd = fuzzle.xpath('//strong/text()')

        # Will not use
        # address  = fuzzle.xpath('//div[@class="gmap-adresse"]/text()')[0]
        self.latitude  = float(data[0])
        self.longitude = float(data[1])
        self.name      = num_name[1]
        self.extra     = {
            'uid': int(num_name[0])
        }
        if len(bikes_places_upd) > 1:
            self.bikes     = int(bikes_places_upd[0])
            self.free      = int(bikes_places_upd[1])
            self.extra['status'] = 'online'
        else:
            self.bikes = 0
            self.free = 0
            self.extra['status'] = 'offline'


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
            station = KeolisStation_v2(marker, self.station_url)
            stations.append(station)
        self.stations = stations

class KeolisStation_v2(BikeShareStation):
    def __init__(self, marker, station_url):
        super(KeolisStation_v2, self).__init__()

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

