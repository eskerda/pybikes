# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from lxml import etree

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


def str2bool(v):
    return v.lower() in ["yes", "true", "t", "1"]


class BixiSystem(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Bixi',
        'company': ['PBSC']
    }

    def __init__(self, tag, feed_url, meta):
        super( BixiSystem, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        scraper = scraper or PyBikesScraper()
        xml_data = scraper.request(self.feed_url)
        dom = etree.fromstring(xml_data.encode('utf-8'))
        markers = dom.xpath('/stations/station')
        self.stations = list(map(BixiStation.from_xml, markers))


class BixiStation(BikeShareStation):
    def __init__(self):
        super(BixiStation, self).__init__()

    @staticmethod
    def from_xml(xml_data):
        """ xml marker object as in
        <station>
            <id>1</id>
            <name>Notre Dame / Place Jacques Cartier</name>
            <terminalName>6001</terminalName>
            <lat>45.508183</lat>
            <long>-73.554094</long>
            <installed>true</installed>
            <locked>false</locked>
            <installDate>1276012920000</installDate>
            <removalDate />
            <temporary>false</temporary>
            <nbBikes>14</nbBikes>
            <nbEmptyDocks>17</nbEmptyDocks>
        </station>
        """
        station = BixiStation()
        terminalName = xml_data.findtext('terminalName')
        name = xml_data.findtext('name')
        latestUpdateTime = xml_data.findtext('latestUpdateTime')

        station.name = "%s - %s" % (terminalName, name)
        station.latitude = float(xml_data.findtext('lat'))
        station.longitude = float(xml_data.findtext('long'))
        station.bikes = int(xml_data.findtext('nbBikes'))
        station.free = int(xml_data.findtext('nbEmptyDocks'))

        station.extra = {
            'uid': int(xml_data.findtext('id')),
            'name': name,
            'terminalName' : terminalName,
            'locked': str2bool(xml_data.findtext('locked')),
            'installed': str2bool(xml_data.findtext('installed')),
            'temporary': str2bool(xml_data.findtext('temporary')),
            'installDate': xml_data.findtext('installDate'),
            'removalDate': xml_data.findtext('removalDate')
        }

        if latestUpdateTime is not None and latestUpdateTime != '0':
            station.extra['latestUpdateTime'] = latestUpdateTime

        return station
