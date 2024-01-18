# -*- coding: utf-8 -*-
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json
from lxml import etree

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import Bounded


class Xian(Bounded, BikeShareSystem):
    headers = {
        'Content-Type': 'text/xml; charset=utf-8'
    }

    def __init__(self, tag, meta, endpoint, bbox=None):
        super(Xian, self).__init__(tag, meta, bounds=bbox)
        self.endpoint = endpoint

    def update(self, scraper=None):
        payload = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:q0="http://ws.itcast.cn/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <soapenv:Body>
                    <q0:findBikeSites></q0:findBikeSites>
                </soapenv:Body>
            </soapenv:Envelope>"""

        scraper = scraper or PyBikesScraper()
        raw = scraper.request(self.endpoint,
                               data=payload,
                               headers=self.headers,
                               method='POST')

        # json encoded inside an xml
        tree = etree.XML(raw.encode('utf-8'))
        stations_xml = tree.xpath('string(//ns1:out)', namespaces={'ns1': 'http://inter.webservice.web.ptpportal.guloo.org'}).replace(' ', '')
        data = json.loads(stations_xml)

        stations = []
        for station_data in data:
            station = XianStation(station_data)
            stations.append(station)

        self.stations = stations


class XianStation(BikeShareStation):
    def __init__(self, data):
        super(XianStation, self).__init__()

        self.name = data['sitename']
        self.latitude = float(data['latitude'])
        self.longitude = float(data['longitude'])

        slots = int(data['locknum'])
        free = int(data['emptynum'])
        self.bikes = slots - free
        self.free = free

        self.extra = {
            'uid': data['siteid'],
            'slots': int(data['locknum']),
            'address': data["location"]
        }
