# -*- coding: utf-8 -*-

from xml.dom import minidom

from base import BikeShareSystem, BikeShareStation
import utils

class BixiSystem(BikeShareSystem):

    feed_url = "https://{system}.bixi.com/data/bikeStations.xml"
    sync = True

    meta = dict(BikeShareSystem.meta, **{'company': 'PBSC'})

    def update(self):

        xml_data = self.scrapper.request(self.feed_url).read()
        dom = minidom.parseString(xml_data)
        markers = dom.getElementsByTagName('station')
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

        terminalName = unicode(utils.getTextTag(xml_data, 'terminalName'))
        name = unicode(utils.getTextTag(xml_data, 'name'))
        self.name = "%s - %s" % (terminalName, name)

        self.latitude = float(utils.getTextTag(xml_data, 'lat'))
        self.longitude = float(utils.getTextTag(xml_data, 'long'))

        self.bikes = int(utils.getTextTag(xml_data, 'nbBikes'))
        self.free = int(utils.getTextTag(xml_data, 'nbEmptyDocks'))

        self.extra = {
            'uid': int(utils.getTextTag(xml_data, 'id')),
            'name' : name,
            'terminalName' : terminalName,
            'locked': utils.str2bool(utils.getTextTag(xml_data, 'locked')),
            'installed': utils.str2bool(utils.getTextTag(xml_data, 'installed')),
            'temporary': utils.str2bool(utils.getTextTag(xml_data, 'temporary')),
            'installDate': utils.getTextTag(xml_data, 'installDate'),
            'removalDate': utils.getTextTag(xml_data, 'removalDate'),
            'latestUpdateTime': utils.getTextTag(xml_data, 'latestUpdateTime'),
        }

class Bixi(BixiSystem):

    feed_url = BixiSystem.feed_url.format(system = 'montreal')

    meta = dict(BixiSystem.meta, **{
            'name': 'Bixi',
            'city': 'Montreal',
            'country': 'CAN',
            'latitude': 45.5086699,
            'longitude': -73.5539925 
            })

    tag = 'bixi'

class CapitalBikeShare(BixiSystem):

    feed_url = 'http://capitalbikeshare.com/data/stations/bikeStations.xml'

    meta = dict(BixiSystem.meta, **{
        'name': 'Capital BikeShare',
        'city': 'Washington, DC - Arlington, VA',
        'country': 'USA',
        'latitude': 38.8951118,
        'longitude': -77.0363658
        })

    tag = 'cabi'
