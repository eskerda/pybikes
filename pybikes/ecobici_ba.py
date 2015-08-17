# -*- coding: utf-8 -*-
# Copyright (C) 2015, eskerda <ustroetz@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from lxml import etree


from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper


FEED_URL = 'https://recursos-data.buenosaires.gob.ar/ckan2/ecobici/estado-ecobici.xml'


class EcobiciBA(BikeShareSystem):
    sync = True

    meta = {
        'system': 'ecobici_ba',
        'company': 'Buenos Aires Ciudad'
    }

    def __init__(self, tag, meta):
        super(EcobiciBA, self).__init__(tag, meta)
        self.feed_url = FEED_URL

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()
        data = scraper.request(self.feed_url)
        tree = etree.XML(data.encode('utf-8'))
        stations_XML = tree[0][0][0][0][0]
        stations = []
        for station_XML in stations_XML:
            station           = BikeShareStation()
            uid               = station_XML.find('{http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx}EstacionId').text
            address           = station_XML.find('{http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx}Lugar').text + ' ' + station_XML.find('{http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx}Numero').text

            station.name      = station_XML.find('{http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx}EstacionNombre').text
            station.latitude  = station_XML.find('{http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx}Latitud').text
            station.longitude = station_XML.find('{http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx}Longitud').text
            station.bikes     = int(station_XML.find('{http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx}AnclajesTotales').text)
            station.free      = int(station_XML.find('{http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx}BicicletaDisponibles').text)

            station.extra = {
                'uid': uid,
                'address': address
            }

            if station.latitude and station.longitude:
                station.latitude = float(station.latitude)
                station.longitude = float(station.longitude)
                stations.append(station)

        self.stations = stations
