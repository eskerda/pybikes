# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from pyquery import PyQuery as pq

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['BixiSystem', 'BixiStation']

class BixiSystem(BikeShareSystem):

    feed_url = "{root_url}bikeStations.xml"
    sync = True

    meta = { 
        'system': 'Bixi',
        'company': 'PBSC' 
    }

    def __init__(self, tag, root_url, meta):
        super( BixiSystem, self).__init__(tag, meta)
        self.feed_url = BixiSystem.feed_url.format(root_url = root_url)

    def update(self):

        xml_data = self._scrapper.request(self.feed_url).text
        dom = pq(xml_data.encode('utf-8'), parser = 'xml')
        markers = dom('station')
        stations = []
        
        for index, marker in enumerate(markers):
            station = BixiStation(index)
            station.from_xml(marker)
            stations.append(station)
        
        self.stations = stations



class BixiStation(BikeShareStation):

    def from_xml(self, xml_data):
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
        xml_data = pq(xml_data, parser='xml')
        
        terminalName = xml_data('terminalName').text()
        name = xml_data('name').text()
        self.name = "%s - %s" % (terminalName, name)
        self.latitude = float(xml_data('lat').text())
        self.longitude = float(xml_data('long').text())
        self.bikes = int(xml_data('nbBikes').text())
        self.free = int(xml_data('nbEmptyDocks').text())

        self.extra = {
            'uid': int(xml_data('id').text()),
            'name': name,
            'terminalName' : terminalName,
            'locked': utils.str2bool(xml_data('locked').text()),
            'installed': utils.str2bool(xml_data('installed').text()),
            'temporary': utils.str2bool(xml_data('temporary').text()),
            'installDate': xml_data('installDate').text(),
            'removalDate': xml_data('removalDate').text(),
            'latestUpdateTime': xml_data('latestUpdateTime').text()
        }
        return self